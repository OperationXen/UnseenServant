import json
from copy import copy
from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import DM, CustomUser


class TestDMBanListViews(TestCase):
    """Check basic DM banlist Add/List/Remove functionality"""

    fixtures = ["test_users", "test_dms", "test_ranks"]

    test_data = {"description": "You're going in the fookin book"}

    def test_dm_can_add_banlist_user(self) -> None:
        self.client.login(username="Test DM", password="testpassword")
        dm = DM.objects.get(pk=1)
        self.assertEqual(dm.banlist.all().count(), 0)

        response = self.client.post(reverse("dms-banlist", kwargs={"discord_name": "testuser"}), self.test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("message", response.data)

        dm.refresh_from_db()
        self.assertEqual(dm.banlist.all().count(), 1)
        self.assertEqual(dm.banlist.through.objects.all()[0].user.discord_name, "testuser")

    def test_dm_can_get_banlist(self) -> None:
        self.client.login(username="Test DM", password="testpassword")
        dm = DM.objects.get(pk=1)
        test_user = CustomUser.objects.get(pk=1)
        dm.banlist.add(test_user, through_defaults={"description": "Test add"})
        dm.save()

        response = self.client.get(reverse("dms-banlist"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("discord_name", response.data[0])
        self.assertEqual(response.data[0]["discord_name"], test_user.discord_name)

    def test_dm_can_remove_banlist_user(self) -> None:
        self.client.login(username="Test DM", password="testpassword")
        dm = DM.objects.get(pk=1)
        test_user = CustomUser.objects.get(pk=1)
        dm.banlist.add(test_user, through_defaults={"description": "Test add"})
        dm.save()
        self.assertEqual(dm.banlist.all().count(), 1)

        response = self.client.delete(reverse("dms-banlist", kwargs={"discord_name": "testuser"}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        dm.refresh_from_db()
        self.assertEqual(dm.banlist.all().count(), 0)

    def test_unauthenticated_user_cannot_see_banlist(self) -> None:
        response = self.client.get(reverse("dms-banlist"))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_non_dm_user_cannot_see_banlist(self) -> None:
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("dms-banlist"))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
