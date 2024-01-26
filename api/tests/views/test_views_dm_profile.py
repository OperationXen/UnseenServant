import json
from copy import copy
from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models.dm import DM


class TestDMProfileViews(TestCase):
    """Check basic DM profile CRUD functionality"""

    fixtures = ["test_users", "test_dms", "test_ranks"]

    def test_list_dms(self) -> None:
        """Check that a user can list all DMs"""
        self.client.logout()

        response = self.client.get(reverse("dms-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
