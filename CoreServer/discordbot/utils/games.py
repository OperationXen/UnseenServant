from discord.ui import Button

def is_button(element):
    return type(element) is Button

def get_game_from_message(message):
    """ Given a generic game, attempt to determine the game it refers to if any """
    try:
        # Iterate through children (actionrows)
        for row in message.components:
            # Individual elements of action rows (buttons)
            for element in filter(lambda x: is_button, row.children):
                print(element)
    except Exception as e:
        print(e)
