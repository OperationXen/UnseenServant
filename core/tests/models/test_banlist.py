from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import DM, CustomUser


class ModelTestBanlist(TestCase):
    """Test the banlist model"""

    fixtures = ["test_dms", "test_users", "test_ranks"]

    def test_banlist_add(self) -> None:
        """Test that a user can be added to a DM's banlist"""
        test_dm = DM.objects.get(pk=1)
        test_user = CustomUser.objects.get(pk=1)

        self.assertEqual(test_dm.banlist.count(), 0)
        test_dm.banlist.add(test_user)
        self.assertEqual(test_dm.banlist.count(), 1)
