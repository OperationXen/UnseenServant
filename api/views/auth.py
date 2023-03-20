from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, logout, login
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework.status import *

from api.serialisers.auth import UserSerialiser

UserModel = get_user_model()


class LoginUser(APIView):
    """Allows a user to authenticate their session"""

    def post(self, request) -> Response:
        """Handle a login request"""
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"message": "Invalid login attempt"}, status=HTTP_400_BAD_REQUEST)
        # Attempt to verify the credentials
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            authed_user = UserSerialiser(user)
            return Response(authed_user.data, status=HTTP_200_OK)
        else:
            return Response({"message": "Invalid credentials or unverified account"}, status=HTTP_401_UNAUTHORIZED)


class LogoutUser(APIView):
    """Allows a user to tear down their existing session"""

    def post(self, request) -> Response:
        """Handle a logout request (only POST allowed)"""
        logout(request)
        return Response({"message": "Logged out"}, HTTP_200_OK)


class RegisterUser(APIView):
    """Allows users to register with the system"""

    def post(self, request) -> Response:
        """Receive and handle a registration request"""
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('password')
        discord_id = request.data.get('discord_id')
        
        user = UserModel.objects.create_user(username=username, password=password, email=email)
        user.discord_id = discord_id
        user.save()
        new_user = UserSerialiser(user)
        return Response(new_user.data, status=HTTP_200_OK)


class ChangeUserPassword(APIView):
    """Allows a logged in user to change their own password"""

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request) -> Response:
        """Handle the password change request"""
        old_pass = request.data.get("oldPass")
        password1 = request.data.get("newPass1")
        password2 = request.data.get("newPass2")

        if not request.user.check_password(old_pass):
            return Response({"message": "Invalid credentials"}, HTTP_401_UNAUTHORIZED)
        if password1 != password2:
            return Response({"message": "Passwords do not match"}, HTTP_400_BAD_REQUEST)
        try:
            validate_password(password1)
            request.user.set_password(password1)
            request.user.save()
            return Response({"message": "Password updated successfully"}, HTTP_200_OK)
        except ValidationError as ve:
            return Response({"message": ve.messages}, HTTP_400_BAD_REQUEST)
