from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

from core.models import Game, DM, Player


class TestStatisticView(TestCase):
    """Parent class to hold utilities"""

    def create_game_yesterday(self) -> Game:
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        dm = DM.objects.get(pk=1)
        new_game = Game.objects.create(datetime=yesterday, name="Yesterdays game", dm=dm)
        return new_game


class TestStatisticGameView(TestStatisticView):
    """Test statistics views for game information"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def test_get_game_statistics_empty(self) -> None:
        """Test that game statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats-games"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_last_month", response.data)
        self.assertEqual(response.data["games_in_last_month"], 0)

    def test_get_game_statistics_one(self) -> None:
        """Test that game statistics show 1 games if 1 games played"""
        self.create_game_yesterday()
        response = self.client.get(reverse("stats-games"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_last_month", response.data)
        self.assertEqual(response.data["games_in_last_month"], 1)


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
        Player.objects.create(game=game, standby=False, discord_id="0001", discord_name="player1")
        Player.objects.create(game=game, standby=False, discord_id="0002", discord_name="player2")
        Player.objects.create(game=game, standby=False, discord_id="0003", discord_name="player3")
        Player.objects.create(game=game, standby=False, discord_id="0004", discord_name="player4")
        Player.objects.create(game=game, standby=False, discord_id="0005", discord_name="player5")
        Player.objects.create(game=game, standby=True, discord_id="1001", discord_name="waitlist1", waitlist=1)
        Player.objects.create(game=game, standby=True, discord_id="1002", discord_name="waitlist2", waitlist=2)
        Player.objects.create(game=game, standby=True, discord_id="1003", discord_name="waitlist3", waitlist=3)

        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("active_users", response.data)
        self.assertEqual(response.data["active_users"], 8)
        self.assertIn("total_players", response.data)
        self.assertEqual(response.data["total_players"], 5)
        self.assertIn("unique_players", response.data)
        self.assertEqual(response.data["unique_players"], 5)

    def test_player_statistics_unselected(self) -> None:
        """Check that the calculation for unselected player numbers is sane"""
        game1 = self.create_game_yesterday()
        game2 = self.create_game_yesterday()
        # Each game has one player
        Player.objects.create(game=game1, standby=False, discord_id="0001", discord_name="player1")
        Player.objects.create(game=game2, standby=False, discord_id="0002", discord_name="player2")
        # One user is waitlisted for both games
        Player.objects.create(game=game1, standby=True, discord_id="1001", discord_name="waitlist1", waitlist=1)
        Player.objects.create(game=game2, standby=True, discord_id="1001", discord_name="waitlist1", waitlist=1)
        # Player 1 is also waitlisted for game 2
        Player.objects.create(game=game2, standby=True, discord_id="0001", discord_name="player1", waitlist=2)

        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("total_unselected_players", response.data)
        self.assertEqual(response.data["total_unselected_players"], 1)


class TestStatisticGenericView(TestStatisticView):
    """Test statistics views for player information"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def test_get_player_statistics_empty(self) -> None:
        """Test that player statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_last_month", response.data)
        self.assertIn("active_users", response.data)
        self.assertIn("unique_players", response.data)
        self.assertIn("games_per_player", response.data)
        self.assertIn("total_unselected_players", response.data)
