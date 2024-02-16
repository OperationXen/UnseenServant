from django.test import TestCase

from core.models.players import Player, Game


class ModelTestPlayers(TestCase):
    """Test the players models"""

    fixtures = ["test_dms", "test_games", "test_users", "test_ranks"]
