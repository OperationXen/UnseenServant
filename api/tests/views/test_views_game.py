from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import Game


class TestGameViews(TestCase):
    """ Check basic game CRUD functionality """
    fixtures=['test_games', 'test_dms', 'test_players']

    def test_list_games(self) -> None:
        """ Check that a user can list upcoming games """
        self.client.logout()
        game = Game.objects.get(pk=1)
        game.datetime = datetime.now() + timedelta(days=1)
        game.save()

        response = self.client.get(reverse('games-list'))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn('name', response.data[0])
        self.assertEqual('Test', response.data[0].get('name'))
        self.assertIn('players', response.data[0])
        self.assertIsInstance(response.data[0].get('players'), list)
