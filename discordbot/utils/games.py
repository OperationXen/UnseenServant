import re
from discord.ui import Button

from discordbot.logs import logger as log
from discordbot.bot import bot


def is_button(element):
    return type(element) is Button


def get_game_number(input):
    """Retrieve a game number from a string"""
    result = re.search("(\d+)", input)
    if result:
        return int(result.group(1))
    return None


def get_game_id_from_message(message):
    """Given a generic message, attempt to determine the ID of the game it refers to [if any]"""
    try:
        for row in message.components:
            for button in filter(lambda x: is_button, row.children):
                if not button.custom_id:
                    continue
                game_id = get_game_number(button.custom_id)
                if game_id:
                    return game_id
        return None
    except Exception as e:
        print(e)

async def _get_game_control_view_for_game(game):
    """ Given a game object, check its mustering channel and retrieve the view attached to the mustering embed"""
    for view in bot.persistent_views:
        view_name = str(type(view))
        if 'GameControlView' in view_name and view.game == game:
            return view
    return None

async def update_game_listing_embed(game):
    """ Refresh a game listing embed for a specific game """
    try:
        view = await _get_game_control_view_for_game(game)
        if view:
            return await view.update_message()
    except Exception as e:
        log.debug(f"Error when updating associated game listing embed")
    return False
