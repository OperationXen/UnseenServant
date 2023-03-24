from copy import copy

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import *

UserModel = get_user_model()


class TestUserLogin(TestCase):
    """Check login functionality"""

    fixtures = ["test_users", "test_ranks"]

    valid_data = {
        "username": "testuser1",
        "password": "testpassword",
    }

    def test_cannot_login_blank_user(self) -> None:
        """Ensure that a blank login attempt fails cleanly"""
        response = self.client.post(reverse("login"), {})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("Invalid login attempt", response.data["message"])
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_cannot_login_user_with_invalid_password(self) -> None:
        """Ensure that an incorrect login attempt fails"""
        test_data = copy(self.valid_data)
        test_data["password"] = "incorrect_password"

        response = self.client.post(reverse("login"), test_data)
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertIn("message", response.data)
        self.assertIn("Invalid credentials", response.data["message"])
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_cannot_enumerate_users(self) -> None:
        """Test that an invalid username looks the same as an invalid password"""
        test_data1 = copy(self.valid_data)
        test_data2 = copy(self.valid_data)
        test_data1["password"] = "incorrect_password"
        test_data2["username"] = "invalid_username"

        response1 = self.client.post(reverse("login"), test_data1)
        self.assertEqual(response1.status_code, HTTP_401_UNAUTHORIZED)
        self.assertFalse(response1.wsgi_request.user.is_authenticated)
        response2 = self.client.post(reverse("login"), test_data1)
        self.assertEqual(response2.status_code, HTTP_401_UNAUTHORIZED)
        self.assertFalse(response2.wsgi_request.user.is_authenticated)
        self.assertEqual(response1.data, response2.data)

    def test_can_login_valid_user_username(self) -> None:
        """A valid user can log in with their username"""
        test_data = copy(self.valid_data)

        response = self.client.post(reverse("login"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("discord_name", response.data)
        self.assertEqual(response.data["username"], test_data["username"])
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_can_login_valid_user_email(self) -> None:
        """A valid user can log in with their email"""
        test_data = copy(self.valid_data)
        test_data["username"] = "testuser1@localhost"

        response = self.client.post(reverse("login"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_returns_user_data(self) -> None:
        """When you log in, the system should return a load of user metadata"""
        test_data = copy(self.valid_data)

        response = self.client.post(reverse("login"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("discord_name", response.data)
        self.assertEqual(response.data["username"], "testuser1")
        self.assertEqual(response.data["email"], "testuser1@localhost")


class TestUserLogout(TestCase):
    """Check logout functionality"""

    fixtures = ["test_users", "test_ranks"]

    def test_can_logout_authed_user(self) -> None:
        """Ensure that a logged in user is properly logged out"""
        logged_in = self.client.login(username="testuser1", password="testpassword")
        self.assertTrue(logged_in)

        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("Logged out", response.data["message"])
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_unauthed_logout(self) -> None:
        """Check that a logout from an unauthenticated user is handled gracefully"""
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("Logged out", response.data["message"])
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TestUserChangePassword(TestCase):
    """Check logged in password update functionality"""

    fixtures = ["test_users", "test_ranks"]

    valid_data = {
        "oldPass": "testpassword",
        "newPass1": "updatedpassword",
        "newPass2": "updatedpassword",
    }

    def test_require_logged_in_user(self) -> None:
        """Ensure that a an anonymous user is given a 403"""
        response = self.client.post(reverse("change_password"), self.valid_data)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_cannot_update_user_with_invalid_password(self) -> None:
        """Ensure that an incorrect password update attempt fails"""
        self.client.login(username="testuser1", password=self.valid_data["oldPass"])
        test_data = copy(self.valid_data)
        test_data["oldPass"] = "incorrect_password"

        response = self.client.post(reverse("change_password"), test_data)
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertIn("message", response.data)
        self.assertIn("Invalid credentials", response.data["message"])
        user = UserModel.objects.get(username="testuser1")
        self.assertFalse(user.check_password(test_data["newPass2"]))

    def test_cannot_update_user_with_mismatching_passwords(self) -> None:
        """Both passwords must be the same"""
        self.client.login(username="testuser1", password=self.valid_data["oldPass"])
        test_data = copy(self.valid_data)
        test_data["newPass1"] = "incorrect_password"

        response = self.client.post(reverse("change_password"), test_data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertIn("Passwords do not match", response.data["message"])
        user = UserModel.objects.get(username="testuser1")
        self.assertFalse(user.check_password(test_data["newPass2"]))

    def test_cannot_update_user_to_weak_password(self) -> None:
        """Password must adhere to minimum requirements (violates multiple constraints)"""
        self.client.login(username="testuser1", password=self.valid_data["oldPass"])
        test_data = copy(self.valid_data)
        test_data["newPass1"] = "123"
        test_data["newPass2"] = "123"

        response = self.client.post(reverse("change_password"), test_data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(type(response.data["message"]), list)
        self.assertGreater(len(response.data["message"]), 0)
        user = UserModel.objects.get(username="testuser1")
        self.assertFalse(user.check_password(test_data["newPass2"]))

    def test_cannot_update_user_to_common_password(self) -> None:
        """Password must adhere to minimum requirements (violates numeric constraint only)"""
        self.client.login(username="testuser1", password=self.valid_data["oldPass"])
        test_data = copy(self.valid_data)
        test_data["newPass1"] = "10191101911019110191"
        test_data["newPass2"] = "10191101911019110191"

        response = self.client.post(reverse("change_password"), test_data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
        self.assertEqual(type(response.data["message"]), list)
        self.assertEqual(len(response.data["message"]), 1)
        self.assertIn("numeric", response.data["message"][0])
        user = UserModel.objects.get(username="testuser1")
        self.assertFalse(user.check_password(test_data["newPass2"]))

    def test_can_update_user_password(self) -> None:
        """Check that a user can update their password successfully"""
        self.client.login(username="testuser1", password=self.valid_data["oldPass"])
        test_data = copy(self.valid_data)

        response = self.client.post(reverse("change_password"), test_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertGreater(len(response.data["message"]), 0)

        user = UserModel.objects.get(username="testuser1")
        self.assertFalse(user.check_password(test_data["oldPass"]))
        self.assertTrue(user.check_password(test_data["newPass2"]))
