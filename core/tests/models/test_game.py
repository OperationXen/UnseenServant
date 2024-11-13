from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import Game, DM


class ModelTestGame(TestCase):
    """Test the game model"""

    fixtures = ["test_dms", "test_games", "test_users", "test_ranks"]

    def test_game_creation(self) -> None:
        """Test that a game object can be created and is sane"""
        test_dm = DM.objects.get(pk=1)
        game_time = timezone.now() + timedelta(days=7)

        game = Game.objects.create(dm=test_dm, name="test game", datetime=game_time)
        self.assertIsInstance(game, Game)
        self.assertEqual(game.signup_type, Game.SignUpTypes.DEFAULT)

    def test_game_tabletop(self) -> None:
        """Test a tabletop can be set on a game"""
        test_string = "http://foundry.com/test"
        test_game = Game.objects.get(pk=1)
        test_game.tabletop = test_string
        test_game.save()

        test_game.refresh_from_db()
        self.assertEqual(test_game.tabletop, test_string)
