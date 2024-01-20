from django.test import TestCase
from django.contrib.auth import get_user_model

from core.utils.user import get_user_max_credit

UserModel = get_user_model()


class MockUser:
    """A lightweight mockup of the discord user object for testing"""

    def __init__(self, id, name, roles):
        self.id = id
        self.name = name
        self.roles = roles


class TestUtilitiesUser(TestCase):
    """Tests for user specific utility functions"""

    fixtures = ["test_ranks", "test_users", "test_bonus_credits"]

    def test_get_user_max_credit(self) -> None:
        """Get max user credit works"""
        user = UserModel.objects.get(username="testuser1")

        max_credit = get_user_max_credit(user)
        self.assertEqual(max_credit, 10)

    def test_get_user_max_credit_with_no_ranks(self) -> None:
        """Check that this doesn't fail if use has no ranks"""
        user = UserModel.objects.get(username="norankuser")

        max_credit = get_user_max_credit(user)
        self.assertEqual(max_credit, 0)
