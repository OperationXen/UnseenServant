import json
import requests

from config.settings import MOONSEACODEX_APIKEY

def get_msc_characters(discord_id: str) -> list:
    """ Retrieve all characters for a given discord user """
    data={'apikey': MOONSEACODEX_APIKEY, 'discord_id': discord_id}

    response = requests.post('https://digitaldemiplane.com/moonseacodex/api/discord_lookup/character/', data=data)
    return json.loads(response.text)
