import json
from copy import copy
from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import Game


class TestGameViews(TestCase):
    """Check basic game CRUD functionality"""

    fixtures = ["test_games", "test_users", "test_dms", "test_players", "test_ranks"]

    valid_data = {
        "name": "New Test Game",
        "module": "CCC-GHC-09",
        "realm": "Forgotten Realms",
        "variant": "Resident AL",
        "description": "Lorem ipsum sit dolor amet",
        "max_players": 4,
        "level_min": 1,
        "level_max": 4,
        "warnings": "Beware of the Leopard",
        "streaming": False,
        "datetime_release": datetime.now(),
        "datetime_open_release": (datetime.now() + timedelta(days=1)),
        "datetime": (datetime.now() + timedelta(days=7)),
        "length": "2 hours",
        "ready": True,
    }

    def test_list_games(self) -> None:
        """Check that a user can list upcoming games"""
        self.client.logout()
        game = Game.objects.get(pk=1)
        game.datetime = datetime.now() + timedelta(days=1)
        game.save()

        response = self.client.get(reverse("games-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertIn("name", response.data[0])
        self.assertEqual("Test", response.data[0].get("name"))
        self.assertIn("players", response.data[0])
        self.assertIsInstance(response.data[0].get("players"), list)
        self.assertIn("discord_id", response.data[0]["players"][0])

    def test_anonymous_user_cant_create_game(self) -> None:
        """An anonymous user should get a 403 error"""
        self.client.logout()
        test_data = copy(self.valid_data)

        num_initial = Game.objects.all().count()

        response = self.client.post(reverse("games-list"), test_data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(num_initial, Game.objects.all().count())

    def test_user_can_create_game(self) -> None:
        """A logged in DM user should be able to create a game"""
        self.client.login(username="Test DM", password="testpassword")
        test_data = copy(self.valid_data)

        response = self.client.post(reverse("games-list"), test_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertIn("name", response.data)
        self.assertEqual(response.data.get("name"), test_data["name"])

    def test_dm_can_update_game(self) -> None:
        """A logged in user can update their own games"""
        self.client.login(username="Test DM", password="testpassword")
        update_data = {"name": "Updated game"}

        response = self.client.patch(
            reverse("games-detail", kwargs={"pk": 2}), json.dumps(update_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertEqual(response.data.get("name"), update_data["name"])

    def test_dm_can_delete_game(self) -> None:
        """A logged in DM should be able to delete their own games"""
        self.client.login(username="Test DM", password="testpassword")

        response = self.client.delete(reverse("games-detail", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        with self.assertRaises(Game.DoesNotExist):
            game = Game.objects.get(pk=2)

    def test_user_cannot_delete_game(self) -> None:
        """A logged in user should be able to delete arbitrary games"""
        self.client.login(username="testuser1", password="testpassword")

        response = self.client.delete(reverse("games-detail", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
