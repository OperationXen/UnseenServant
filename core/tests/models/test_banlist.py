from django.test import TestCase

from core.models import DM, CustomUser, DMBanList


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

    def test_banlist_string(self) -> None:
        test_dm = DM.objects.get(pk=1)
        test_user = CustomUser.objects.get(pk=1)

        ban = DMBanList.objects.create(dm=test_dm, user=test_user, description="test ban")
        self.assertIsInstance(ban, DMBanList)
        self.assertIn(test_dm.user.discord_name, str(ban))
        self.assertIn(test_user.discord_name, str(ban))
