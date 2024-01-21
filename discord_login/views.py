import requests
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.status import *
from rest_framework.views import Request
import base64
import json
import uuid

from discord_bot.logs import logger as log

from config.settings import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_GUILDS
from config.settings import AUTH_COMPLETE_URL, AUTH_FAIL_URL, AUTH_REDIRECT_URL

auth_url_discord = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={AUTH_REDIRECT_URL}&response_type=code&scope=identify%20guilds%20guilds.members.read"


def discord_login(request: Request) -> redirect:
    """Redirect user to discord login page"""
    state_id = str(uuid.uuid4())
    request.session['oauth_state'] = state_id
    referer = request.META.get('HTTP_REFERER', AUTH_COMPLETE_URL)
    state_data = { 'referer': referer, 'id': state_id}
    state_json = json.dumps(state_data)
    state = base64.b64encode(state_json.encode()).decode('utf-8')
    return redirect(f"{auth_url_discord}&state={state}")


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
        "redirect_uri": AUTH_REDIRECT_URL,
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
    state = request.GET.get("state", None)
    if state:
        decoded_state = base64.b64decode(state.encode()).decode('utf-8')
        state_dict = json.loads(decoded_state)
        state_id = state_dict.get('id', None)
        stored_state_id = request.session.get('oauth_state', None)
        if state_id is None or state_id != stored_state_id:
            log.error("return id from discord does not match stored one, possible hijack")
        else:
            code = request.GET.get("code")
            if code:
                user_data = exchange_code(code)
                if user_data:
                    discord_user = authenticate(request, user_data=user_data["user"], roles=user_data["roles"])
                    if discord_user:
                        login(request, discord_user)
                        webapp_redirect  = state_dict.get('referer', AUTH_COMPLETE_URL)
                        return redirect(webapp_redirect)
                    else:
                        log.error("User failed authentication")
                else:
                    log.error("Unable to exchange supplied code for token")
            else:
                log.error("Unable to get code from request")
    else :
        log.error("No state in discord return, possible hijack")
    return redirect(AUTH_FAIL_URL)


def discord_auth_complete(request: Request) -> JsonResponse:
    """fallback view for showing a successful login"""
    return JsonResponse({"message": "Authenticated via discord"}, status=HTTP_200_OK)


def discord_auth_failed(request: Request) -> JsonResponse:
    """fallback view for showing a failed login"""
    return JsonResponse({"message": "Authentication failed"}, status=HTTP_401_UNAUTHORIZED)
