from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

from core.models import Rank, BonusCredit
from core.utils.players import get_player_max_games, get_user_highest_rank, get_bonus_credits


class MockUser:
    """A lightweight mockup of the discord user object for testing"""

    def __init__(self, id, name, roles):
        self.id = id
        self.name = name
        self.roles = roles


class TestUtilitiesPlayer(TestCase):
    """Tests for user specific utility functions"""

    fixtures = ["test_ranks", "test_users", "test_bonus_credits"]
    mock_user = MockUser(id=1234567890, name="Mockuser", roles=["11111111", "22222222"])

    def test_get_user_rank_valid(self) -> None:
        """Check we can get a user rank for a known-good role name"""
        rank = get_user_highest_rank(
            [
                "22222222",
            ]
        )
        self.assertIsInstance(rank, Rank)
        self.assertEqual(rank.priority, 5)
        self.assertEqual(rank.max_games, 1)

    def test_get_user_rank_invalid(self) -> None:
        """Check we can get a user rank for a known-bad role name"""
        rank = get_user_highest_rank(
            [
                "123123123",
            ]
        )
        self.assertIsNone(rank)

    def test_get_bonus_credits(self) -> None:
        """Test the retrieval of bonus credits for a user"""
        bonus_credit = BonusCredit.objects.get(pk=1)
        bonus_credit.expires = timezone.now() + timedelta(hours=1)
        bonus_credit.save()

        credits = get_bonus_credits("12345678900987654321")
        self.assertIsInstance(credits, int)
        self.assertEqual(credits, bonus_credit.credits)

    def test_get_player_max_games(self) -> None:
        """Test the get max player function"""
        games = get_player_max_games(self.mock_user)
        self.assertIsInstance(games, int)
        self.assertEqual(games, 10)
