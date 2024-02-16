from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

from core.models import Game, DM, Player, CustomUser


class TestStatisticView(TestCase):
    """Parent class to hold utilities"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def create_game_yesterday(self) -> Game:
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        dm = DM.objects.get(pk=1)
        new_game = Game.objects.create(datetime=yesterday, name="Yesterdays game", dm=dm)
        return new_game


class TestStatisticGameView(TestStatisticView):
    """Test statistics views for game information"""

    def test_get_game_statistics_empty(self) -> None:
        """Test that game statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats-games"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_specified_period", response.data)
        self.assertEqual(response.data["games_in_specified_period"], 0)

    def test_get_game_statistics_one(self) -> None:
        """Test that game statistics show 1 games if 1 games played"""
        self.create_game_yesterday()
        response = self.client.get(reverse("stats-games"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_specified_period", response.data)
        self.assertEqual(response.data["games_in_specified_period"], 1)

    def test_get_game_statistics_parameters(self) -> None:
        """check the statistics endpoint handles day parameters"""
        self.client.login(username="admin", password="testpassword")
        response = self.client.get(reverse("stats-games"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 42)

    def test_get_game_statistics_parameters_auth(self) -> None:
        """check the statistics endpoint ignores day parameters from non-superusers"""
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("stats-games"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 31)


class TestStatisticPlayerView(TestStatisticView):
    """Test statistics views for player information"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def test_get_player_statistics(self) -> None:
        """Test that game statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats-players"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("active_users", response.data)
        self.assertIn("unique_players", response.data)
        self.assertIn("games_per_player", response.data)

    def test_player_statistics_sane(self) -> None:
        """Check that the active users statistic is sane"""
        game = self.create_game_yesterday()
        Player.objects.create(game=game, standby=False, user=CustomUser.objects.get(username="testuser1"))
        Player.objects.create(game=game, standby=False, user=CustomUser.objects.get(username="testuser2"))
        Player.objects.create(game=game, standby=True, waitlist=2, user=CustomUser.objects.get(username="playeruser"))

        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("active_users", response.data)
        self.assertEqual(response.data["active_users"], 3)
        self.assertIn("total_players", response.data)
        self.assertEqual(response.data["total_players"], 2)
        self.assertIn("unique_players", response.data)
        self.assertEqual(response.data["unique_players"], 2)

    def test_player_statistics_unselected(self) -> None:
        """Check that the calculation for unselected player numbers is sane"""
        game1 = self.create_game_yesterday()
        game2 = self.create_game_yesterday()
        # Each game has one player
        Player.objects.create(game=game1, standby=False, user=CustomUser.objects.get(username="testuser1"))
        Player.objects.create(game=game2, standby=False, user=CustomUser.objects.get(username="testuser2"))
        # One user is waitlisted for both games
        Player.objects.create(
            game=game1, standby=True, waitlist=1, user=CustomUser.objects.get(username="waitlistuser")
        )
        Player.objects.create(
            game=game2, standby=True, waitlist=1, user=CustomUser.objects.get(username="waitlistuser")
        )
        # Player 1 is also waitlisted for game 2
        Player.objects.create(game=game2, standby=True, waitlist=2, user=CustomUser.objects.get(username="testuser1"))

        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("total_unselected_players", response.data)
        self.assertEqual(response.data["total_unselected_players"], 1)

    def test_get_player_statistics_parameters(self) -> None:
        """check the statistics endpoint handles day parameters"""
        self.client.login(username="admin", password="testpassword")
        response = self.client.get(reverse("stats-players"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 42)

    def test_get_game_statistics_parameters_auth(self) -> None:
        """check the statistics endpoint ignores day parameters from non-superusers"""
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("stats-players"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 31)


class TestStatisticGenericView(TestStatisticView):
    """Test statistics views for player information"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def test_get_general_statistics_empty(self) -> None:
        """Test that player statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_specified_period", response.data)
        self.assertIn("active_users", response.data)
        self.assertIn("unique_players", response.data)
        self.assertIn("games_per_player", response.data)
        self.assertIn("total_unselected_players", response.data)

    def test_get_general_statistics_parameters(self) -> None:
        """check the statistics endpoint handles day parameters"""
        self.client.login(username="admin", password="testpassword")
        response = self.client.get(reverse("stats"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 42)

    def test_get_general_statistics_parameters_auth(self) -> None:
        """check the statistics endpoint ignores day parameters from non-superusers"""
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("stats"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 31)


class TestStatisticDetailedView(TestStatisticView):
    """Test the detailed viewset"""

    def test_no_unauthorised_access(self) -> None:
        """Ensure that anonymous users cannot see this data"""
        self.client.login()

        response = self.client.get(reverse("stats-detailed"))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_detailed_statistics_parameters(self) -> None:
        """check the detailed statistics endpoint handles day parameters"""
        self.client.login(username="admin", password="testpassword")
        response = self.client.get(reverse("stats-detailed"), {"days": 42})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("days_of_data", response.data)
        self.assertEqual(response.data["days_of_data"], 42)

    def test_get_detailed_statistics_sane(self) -> None:
        """Ensure that the detailed statistics are sane"""
        game1 = self.create_game_yesterday()
        game2 = self.create_game_yesterday()
        user1 = CustomUser.objects.get(username="testuser1")
        user2 = CustomUser.objects.get(username="testuser2")
        waitlist_user = CustomUser.objects.get(username="waitlistuser")

        # Each game has one player
        Player.objects.create(game=game1, standby=False, user=user1)
        Player.objects.create(game=game2, standby=False, user=user2)
        # One user is waitlisted for both games
        Player.objects.create(game=game1, standby=True, user=waitlist_user, waitlist=1)
        Player.objects.create(game=game2, standby=True, user=waitlist_user, waitlist=1)
        # Player 1 is also waitlisted for game 2
        Player.objects.create(game=game2, standby=True, user=user1, waitlist=2)

        self.client.login(username="admin", password="testpassword")
        response = self.client.get(reverse("stats-detailed"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("user_details", response.data)
        user_details = response.data["user_details"]
        self.assertIn("waitlistuser", user_details)
        self.assertEqual(user_details["waitlistuser"], 2)
        self.assertEqual(len(user_details), 1)
