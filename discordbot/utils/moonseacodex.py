import json
import requests

from config.settings import MOONSEACODEX_APIKEY

def _get_rarity_string(x: str) -> str:
    """ Get a user friendly representation of the item rarity """
    if x == 'common':
        return 'Common'
    if x == 'uncommon':
        return 'Uncommon'
    if x == 'rare':
        return 'Rare'
    if x == 'veryrare':
        return 'Very rare'
    if x == 'legendary':
        return 'Legendary'
    if x == 'artefact':
        return 'Artefact'
    return 'Unknown rarity'


def _get_item_string(x: dict) -> str:
    """ get a string representation of a single magic item """
    rarity = _get_rarity_string(x.get('rarity'))

    if x.get('attunement'):
        return f"{x.get('name')} ({rarity}, attuned)"
    return f"{x.get('name')} ({rarity})"

def get_items_string(items: list) -> str:
    """ A string to represent the characters currently equipped items """        
    if items:
        retval = ', \n'.join(_get_item_string(item) for item in items)
    else:
        retval = 'No items equipped'
    return retval

def get_stats_string(x: dict) -> str:
    """ Get a string to represent the characters important statistics """
    retval = f"AC: {x.get('ac')} | HP: {x.get('hp')} | PP: {x.get('pp')} | DC: {x.get('dc')}"
    return retval

def _get_class_string(x: dict) -> str:
    """ Turn a class into a string """
    if x.get('subclass'):
        return f"{x.get('name')} ({x.get('subclass')}) - {x.get('value')}"
    return f"{x.get('name')} - {x.get('value')}"

def get_classes_string(character: dict) -> str:
    """ Process a character object to a representation of it's classes and subclasses """
    retval = " / ".join(_get_class_string(x) for x in character.get('classes'))
    return retval

def get_character_string(character: dict) -> str:
    """ Process a character object to a simple string representation """
    classes = " / ".join(f"{x.get('name')} ({x.get('value')})" for x in character.get('classes'))
    return f"{character.get('name')} - {character.get('race')} {classes}"

def get_msc_characters(discord_id: str) -> list:
    """ Retrieve all characters for a given discord user """
    data={'apikey': MOONSEACODEX_APIKEY, 'discord_id': discord_id}
    response = requests.post('https://digitaldemiplane.com/moonseacodex/api/discord_lookup/character/', data=data)
    return json.loads(response.text)
