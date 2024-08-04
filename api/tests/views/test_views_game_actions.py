from datetime import timedelta

from rest_framework.status import *
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from core.models import Player, Game


class TestGameActionViews(TestCase):
    """Check basic game CRUD functionality"""

    fixtures = ["test_games", "test_users", "test_ranks", "test_dms", "test_players", "test_bans"]

    def test_anonymous_user_cant_join_game(self) -> None:
        """Users must be logged in"""
        self.client.logout()

        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_dm_cant_join_own_game(self) -> None:
        """DMs cannot play in their own games"""
        self.client.login(username="Test DM", password="testpassword")

        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("You cannot play in your own game", response.data["message"])

    def test_credit_required_to_join_game(self) -> None:
        """Players must have sufficient credit"""
        self.client.login(username="nogamesuser", password="testpassword")

        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertIn("message", response.data)
        self.assertTrue("available credit" in response.data["message"])

    def test_banned_user_cant_join(self) -> None:
        """A banned user cannot join any games"""
        self.client.login(username="banneduser", password="testpassword")

        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertIn("message", response.data)
        self.assertIn("banned", response.data["message"])

    def test_user_can_join_game(self) -> None:
        """A user can join a game"""
        self.client.login(username="testuser1", password="testpassword")
        game = Game.objects.get(pk=1)
        player_count = Player.objects.filter(game=game).count()
        self.assertEqual(player_count, 2)

        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["game_name"], game.name)
        self.assertEqual(Player.objects.filter(game=game).count(), player_count + 1)
        last_player = Player.objects.filter(game=game).last()
        self.assertFalse(last_player.standby)  # user not on standby list

    def test_user_waitlisting(self) -> None:
        """Players placed on waitlist if the game is full"""
        self.client.login(username="testuser1", password="testpassword")
        game = Game.objects.get(pk=1)
        self.assertGreaterEqual(Player.objects.filter(game=game).count(), 2)
        game.max_players = 1
        game.save()

        response = self.client.post(reverse("games-join", kwargs={"pk": game.pk}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["game_name"], game.name)
        self.assertEqual(Player.objects.filter(game=game).count(), 3)
        player = Player.objects.filter(game=game).last()
        self.assertTrue(player.standby)
        self.assertGreaterEqual(player.waitlist, 1)

    def test_anonymous_user_cant_leave_game(self) -> None:
        """Users must be logged in"""
        self.client.logout()

        response = self.client.post(reverse("games-drop", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_user_can_leave_game(self) -> None:
        """Players leaving games are refunded their signup credit"""
        game = Game.objects.get(pk=1)
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

        self.client.login(username="playeruser", password="testpassword")
        response = self.client.post(reverse("games-drop", kwargs={"pk": 1}))
        self.assertIn(game.name, response.data["message"])
        self.assertEqual(Player.objects.filter(game=game).count(), 1)

    def test_leave_game_error_message(self) -> None:
        """An error message should be returned if you attempt to leave a game you are not in"""
        game = Game.objects.get(pk=1)
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

        self.client.login(username="nogamesuser", password="testpassword")
        response = self.client.post(reverse("games-drop", kwargs={"pk": 1}))
        self.assertIn("You are not in this game", response.data["message"])
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

    def test_user_cant_leave_old_game(self) -> None:
        """Check that a user cannot leave a game after the first hour"""
        game = Game.objects.get(pk=1)
        # update game time to be two hours ago
        game.datetime = timezone.now() - timedelta(hours=2)
        game.save()
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

        self.client.login(username="playeruser", password="testpassword")
        response = self.client.post(reverse("games-drop", kwargs={"pk": 1}))
        self.assertTrue("message" in response.data)
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

    def test_user_can_leave_just_started_game(self) -> None:
        """Check that a user can leave a game before the first hour passes"""
        game = Game.objects.get(pk=1)
        # update game time to be less than an hour ago
        game.datetime = timezone.now() - timedelta(minutes=55)
        game.save()
        self.assertEqual(Player.objects.filter(game=game).count(), 2)

        self.client.login(username="playeruser", password="testpassword")
        response = self.client.post(reverse("games-drop", kwargs={"pk": 1}))
        self.assertIn(game.name, response.data["message"])
        self.assertEqual(Player.objects.filter(game=game).count(), 1)

    def test_user_cant_join_game_twice(self) -> None:
        """A user who is already in a game cannot join it again"""
        self.client.login(username="playeruser", password="testpassword")
        game = Game.objects.get(pk=1)

        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
