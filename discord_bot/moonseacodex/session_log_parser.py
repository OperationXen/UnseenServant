from discord_bot.moonseacodex.game import Game


def get_game_from_message(message):
    return Game(message.content)
