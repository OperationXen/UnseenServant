from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

from core.models import Game, DM


class TestStatisticGameView(TestCase):
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
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        dm = DM.objects.get(pk=1)
        new_game = Game.objects.create(datetime=yesterday, name="Yesterdays game", dm=dm)

        response = self.client.get(reverse("stats-games"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_last_month", response.data)
        self.assertEqual(response.data["games_in_last_month"], 1)


class TestStatisticPlayerView(TestCase):
    """Test statistics views for player information"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def test_get_player_statistics(self) -> None:
        """Test that game statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats-players"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("all_players", response.data)
        self.assertIn("unique_players", response.data)
        self.assertIn("games_per_player", response.data)


class TestStatisticGenericView(TestCase):
    """Test statistics views for player information"""

    fixtures = ["test_games", "test_dms", "test_users", "test_ranks"]

    def test_get_player_statistics(self) -> None:
        """Test that game statistics show 0 games if 0 games played"""
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("games_in_last_month", response.data)
        self.assertIn("all_players", response.data)
        self.assertIn("unique_players", response.data)
        self.assertIn("games_per_player", response.data)
