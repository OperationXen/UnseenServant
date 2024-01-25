import json
from copy import copy
from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import Game


class TestGameVariantViews(TestCase):
    """Check that the game variant endpoint is functional"""

    def test_list_variant_options(self) -> None:
        """Check that an anonymous user can list all game variants"""
        self.client.logout()

        response = self.client.get(reverse("game-variants-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)


class TestGameRealmViews(TestCase):
    """Check that the game realm endpoint is functional"""

    def test_list_realm_options(self) -> None:
        """Check that an anonymous user can list all valid realms"""
        self.client.logout()

        response = self.client.get(reverse("game-variants-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
