from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import DM, CustomUser, Game


class TestDMBanListGameViews(TestCase):
    fixtures = ["test_games", "test_users", "test_dms", "test_players", "test_ranks"]

    def test_banlisted_user_cannot_join_game(self) -> None:
        """A banlisted user should get a 401 error when siging up for a game"""
        game = Game.objects.get(pk=1)
        test_user = CustomUser.objects.get(username="testuser1")
        game.dm.banlist.add(test_user)
        game.dm.save()

        self.client.login(username="testuser1", password="testpassword")
        response = self.client.post(reverse("games-join", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertIn("message", response.data)
        self.assertFalse(game.players.filter(user=test_user).exists())
