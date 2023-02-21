from django.test import TestCase

from core.models.players import Player, Game


class ModelTestPlayers(TestCase):
    """Test the players models"""

    fixtures = ["test_dms", "test_games", "test_users"]

    def test_discord_id_rounding(self) -> None:
        """As long numbers discord IDs in player objects can be rounded causing problems"""
        long_id_number = "12345678900987654321"

        try:
            game = Game.objects.get(pk=1)
            player = Player(game=game, discord_name="Test Player", discord_id=long_id_number)
            player.save()
            player.refresh_from_db()
            self.assertEqual(player.discord_id, long_id_number)
        except OverflowError as e:
            self.fail("Database cannot handle long ints for discord ID")
