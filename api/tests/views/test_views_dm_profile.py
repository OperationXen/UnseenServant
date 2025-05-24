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

    valid_data = {
        "name": "newDM",
        "description": "new description",
        "rules_text": "new rules text",
        "muster_text": "new muster text",
    }

    def test_list_dms(self) -> None:
        """Check that a user can list all DMs"""
        self.client.logout()

        response = self.client.get(reverse("dms-list"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_current_user_dm_details(self) -> None:
        """Get the DM profile for the current user"""
        self.client.login(username="Test DM", password="testpassword")

        response = self.client.get(reverse("dms-detail", kwargs={"pk": "me"}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertEqual(response.data.get("name"), "Test DM")

    def test_get_current_user_dm_details_failure(self) -> None:
        """Test that a user without a DM profile gets a sensible response"""
        self.client.login(username="testuser1", password="testpassword")

        response = self.client.get(reverse("dms-detail", kwargs={"pk": "me"}))
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_get_current_user_dm_requires_login(self) -> None:
        """Test that a user without a DM profile gets a sensible response"""
        self.client.logout()

        response = self.client.get(reverse("dms-detail", kwargs={"pk": "me"}))
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_get_dm_details(self) -> None:
        """Get detail view of a single DM"""
        self.client.logout()

        response = self.client.get(reverse("dms-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertEqual(response.data.get("name"), "Test DM")
        self.assertIn("discord_id", response.data)
        self.assertEqual(response.data.get("discord_id"), "33333333")

    def test_create_dm_fails_anonymously(self) -> None:
        """Create a new DM"""
        self.client.logout()
        test_data = copy(self.valid_data)

        response = self.client.post(reverse("dms-list"), test_data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_create_dm_fails_for_duplicate(self) -> None:
        """Check that a user who already has a DM entry cannot create a second"""
        self.client.login(username="Test DM", password="testpassword")
        test_data = copy(self.valid_data)
        initial_dm_count = DM.objects.all().count()

        response = self.client.post(reverse("dms-list"), test_data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("already registered", response.data.get("message"))
        dm_count = DM.objects.all().count()
        self.assertEqual(initial_dm_count, dm_count)

    def test_create_dm_succeeds(self) -> None:
        """Test a user can create a DM entry for themselves"""
        self.client.login(username="testuser1", password="testpassword")

        test_data = copy(self.valid_data)
        initial_dm_count = DM.objects.all().count()

        response = self.client.post(reverse("dms-list"), test_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertIn("name", response.data)
        self.assertEqual("newDM", response.data.get("name"))
        self.assertIn("discord_id", response.data)
        self.assertEqual(response.data.get("discord_id"), "11111111")
        self.assertIn("discord_name", response.data)
        self.assertEqual(response.data.get("discord_name"), "testuser1")
        dm_count = DM.objects.all().count()
        self.assertEqual(initial_dm_count + 1, dm_count)

    def test_update_dm_fails_for_invalid_user(self) -> None:
        """Attempting to update a different users dm profile from a non-superuser account fails"""
        self.client.login(username="testuser1", password="testpassword")
        update_data = {"name": "updated DM"}
        dm = DM.objects.get(pk=1)
        initial_name = dm.name

        response = self.client.patch(reverse("dms-detail", kwargs={"pk": 1}), update_data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertIn("message", response.data)
        self.assertIn("permissions", response.data.get("message"))
        dm = DM.objects.get(pk=1)
        self.assertEqual(dm.name, initial_name)

    def test_update_dm_succeeds(self) -> None:
        """A user can update their own DM profile"""
        self.client.login(username="Test DM", password="testpassword")

        update_data = {"name": "updated DM"}
        dm = DM.objects.get(pk=1)
        initial_name = dm.name

        response = self.client.patch(
            reverse("dms-detail", kwargs={"pk": "me"}), json.dumps(update_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("updated DM", response.data.get("name"))
        dm = DM.objects.get(pk=1)
        self.assertEqual(dm.name, "updated DM")

    def test_update_dm_creates_missing(self) -> None:
        """A user without a DM profile updating theirs should have the profile created"""
        self.client.login(username="testuser1", password="testpassword")

        update_data = {"name": "updated DM"}

        response = self.client.patch(
            reverse("dms-detail", kwargs={"pk": "me"}), json.dumps(update_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        dm = DM.objects.get(user__username="testuser1")
        self.assertEqual(dm.name, "updated DM")

    def test_delete_dm_fails_for_invalid_user(self) -> None:
        """Ensure a user cannot delete anyone else's DM profile"""
        self.client.login(username="testuser1", password="testpassword")
        initial_dm_count = DM.objects.all().count()

        response = self.client.delete(reverse("dms-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        dm_count = DM.objects.all().count()
        self.assertEqual(initial_dm_count, dm_count)

    def test_delete_dm_succeeds(self) -> None:
        """Ensure a user can delete their DM profile"""
        self.client.login(username="Test DM", password="testpassword")

        response = self.client.delete(reverse("dms-detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, HTTP_200_OK)
        with self.assertRaises(DM.DoesNotExist):
            dm = DM.objects.get(name="Test DM")
