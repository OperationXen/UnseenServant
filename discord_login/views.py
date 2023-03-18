import requests
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

from config.settings import DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, DISCORD_GUILDS
from rest_framework.views import Response, Request
from rest_framework.status import *

auth_url_discord = 'https://discord.com/api/oauth2/authorize?client_id=930903782089437205&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fdiscord_auth%2Fdone%2F&response_type=code&scope=identify%20guilds'

def discord_login(request: Request) -> redirect:
    """ Redirect user to discord login page """
    return redirect(auth_url_discord)

def exchange_code(code: str):
    """ Exchange the code supplied for a longer term token """
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'http://127.0.0.1:8000/discord_auth/done/',
        'scope': 'identify'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers)
    credentials = response.json()
    access_token = credentials['access_token']

    response = requests.get(f"https://discord.com/api/v10/users/@me/guilds/{DISCORD_GUILDS[0]}/member", headers={'Authorization': f"Bearer {access_token}"})
    user_data = response.json()
    return user_data

def discord_auth_done(request: Request) -> JsonResponse:
    """ view to handle the request made back to us after the user has authenticated against Discord """
    code = request.GET.get('code')
    user_data = exchange_code(code)
    discord_user = authenticate(request, user_data=user_data['user'], roles=user_data['roles'])
    if discord_user:
        login(request, discord_user)
        return JsonResponse({'user': user_data})
    return JsonResponse({'message': 'Failed to authenticate'}, status=HTTP_401_UNAUTHORIZED)
