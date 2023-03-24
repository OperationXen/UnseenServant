from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import *

UserModel = get_user_model()


class TestUserDetails(TestCase):
    """Check user details functionality"""

    fixtures = ["test_users", "test_ranks"]

    def test_get_details_anonymous_user(self) -> None:
        """ An anonymous user should be reflected as such """
        self.client.logout()

        response = self.client.get(reverse('user_details'))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['user_data'], None)

    def test_get_details_valid_user(self) -> None:
        """ A valid user should return sensible results """
        user = UserModel.objects.get(pk=1)
        self.client.force_login(user)

        response = self.client.get(reverse('user_details'))
        self.assertEqual(response.status_code, HTTP_200_OK)
        user_data = response.data['user_data']
        self.assertNotEqual(user_data, None)

        self.assertEqual(user_data['username'], "testuser1")
        self.assertEqual(user_data['email'], 'testuser1@localhost')
        self.assertEqual(user_data['discord_name'], 'testuser#1337')
        self.assertIsNotNone(user_data['ranks'])

        ranks = user_data['ranks']
        self.assertEqual(len(ranks), 1)
        self.assertIsInstance(ranks[0]['name'], str)
        self.assertEqual(ranks[0]['name'], 'Admin')
