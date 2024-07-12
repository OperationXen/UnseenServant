from django.test import TestCase

from core.models import CustomUser, Announcement
from core.utils.announcements import *


class TestUtilitiesAnnouncement(TestCase):
    """Tests for announcement specific utility functions"""

    fixtures = ["test_users", "test_ranks", "test_announcements"]

    def test_personal_announcement(self) -> None:
        """Get personal announcement"""
        user = CustomUser.objects.get(pk=1)
        announcements = get_user_custom_announcements(user)
        self.assertIsInstance(announcements[0], Announcement)
        self.assertIn("personal announcement", announcements[0].text)

    def test_generic_announcement(self) -> None:
        """Get a generic announcement"""
        announcements = get_generic_announcements()
        self.assertIsInstance(announcements[0], Announcement)
        self.assertIn("generic announcement", announcements[0].text)

    def test_text_generation(self) -> None:
        """Ensure text replacement works as expected for user name"""
        user = CustomUser.objects.get(pk=1)
        announcement = Announcement.objects.get(pk=1)
        text = generate_announcement_text(announcement, user)
        self.assertIsInstance(text, str)
        self.assertIn("Test generic announcement testuser", text)

    def test_announcement_generation_personal(self) -> None:
        """Check fetch logic for a user with a personal announcement"""
        user = CustomUser.objects.get(pk=1)
        text = get_player_announce_text(user)
        self.assertIsInstance(text, str)
        self.assertIn("Test personal announcement testuser", text)

    def test_announcement_generation_generic(self) -> None:
        """Check fetch logic for a user without a personal announcement"""
        user = CustomUser.objects.get(pk=2)
        text = get_player_announce_text(user)
        self.assertIsInstance(text, str)
        self.assertIn("Test generic announcement seconduser", text)
