import re
from discord.ui import Button


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
