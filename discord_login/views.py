import requests
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.status import *
from rest_framework.views import Request

from discord_bot.logs import logger as log
from config.settings import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_GUILDS, SERVER_URI
from config.settings import AUTH_COMPLETE_URL, AUTH_FAIL_URL

auth_url_discord = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={SERVER_URI}/discord_auth/done/&response_type=code&scope=identify%20guilds%20guilds.members.read"


def discord_login(request: Request) -> redirect:
    """Redirect user to discord login page"""
    return redirect(auth_url_discord)


def discord_logout(request: Request) -> JsonResponse:
    """Invalidate the user's current session"""
    logout(request)
    return JsonResponse({"message": "logged out"}, status=HTTP_200_OK)


def exchange_code(code: str):
    """Exchange the code supplied for a longer term token"""
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{SERVER_URI}/discord_auth/done/",
        "scope": "identify",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers)
        credentials = response.json()
        access_token = credentials["access_token"]
    except Exception as e:
        log.error("Unable to get OAUTH token")
        return None

    try:
        response = requests.get(
            f"https://discord.com/api/v10/users/@me/guilds/{DISCORD_GUILDS[0]}/member",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = response.json()
        return user_data
    except Exception as e:
        return None


def discord_auth_done(request: Request) -> JsonResponse:
    """view to handle the request made back to us after the user has authenticated against Discord"""
    code = request.GET.get("code")
    if code:
        user_data = exchange_code(code)
        if user_data:
            discord_user = authenticate(request, user_data=user_data["user"], roles=user_data["roles"])
            if discord_user:
                login(request, discord_user)
                return redirect(AUTH_COMPLETE_URL)
            else:
                log.error("User failed authentication")
        else:
            log.error("Unable to exchange supplied code for token")
    else:
        log.error("Unable to get code from request")
    return redirect(AUTH_FAIL_URL)


def discord_auth_complete(request: Request) -> JsonResponse:
    """fallback view for showing a successful login"""
    return JsonResponse({"message": "Authenticated via discord"}, status=HTTP_200_OK)


def discord_auth_failed(request: Request) -> JsonResponse:
    """fallback view for showing a failed login"""
    return JsonResponse({"message": "Authentication failed"}, status=HTTP_401_UNAUTHORIZED)
