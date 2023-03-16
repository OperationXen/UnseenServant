import requests
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

from rest_framework.views import Response, Request
from rest_framework.status import *

auth_url_discord = 'https://discord.com/api/oauth2/authorize?'


# Create your views here.
def home(request: Request) -> Response:
    """ Home page view """
    return Response({'message': 'Home page view'})

def discord_login(request: Request) -> redirect:
    """ Redirect user to discord login page """
    return redirect(auth_url_discord)

def discord_login_done(request: Request) -> Response:
    """ view to handle the request made back to us after the user has authenticated against Discord """
    code = request.GET.get('code')
    print(code)
    user = exchange_code(code)
    discord_user = authenticate(request, user=user)
    if discord_user:
        login(discord_user)
        return Response({'user': user})
    return Response({'message': 'Failed to authenticate'}, status=HTTP_401_UNAUTHORIZED)

def exchange_code(code: str):
    """ Exchange the code supplied for a longer term token """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post("https://discord.com/api/oauth/token", data=data, headers=headers)
    credentials = requests.json()
    access_token = credentials['access_token']

    response = requests.get("https://discord.com/api/v6/users/@me", headers={'Authorization': f"Bearer {access_token}"})
    user_data = response.json()

