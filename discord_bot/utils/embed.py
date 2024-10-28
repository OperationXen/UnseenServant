from discord_bot.bot import bot
from discord_bot.logs import logger as log
from core.models import Game


def async_get_mustering_view_for_game(game: Game):
    """Given a game object, check its mustering channel and retrieve the view attached to the mustering embed"""
    for view in bot.persistent_views:
        view_name = str(type(view))
        if "MusteringView" in view_name and view.game == game:
            return view
    return None


async def async_update_mustering_embed(game: Game):
    """Refresh a mustering embed for a specific game"""
    try:
        view = async_get_mustering_view_for_game(game)
        if view:
            return await view.update_message()
    except Exception as e:
        log.debug(f"Error when updating associated muster embed")
    return False


async def async_get_game_control_view_for_game(game):
    """Given a game object, check its mustering channel and retrieve the view attached to the mustering embed"""
    for view in bot.persistent_views:
        view_name = str(type(view))
        if "GameControlView" in view_name and view.game == game:
            return view
    return None


async def async_update_game_listing_embed(game):
    """Refresh a game listing embed for a specific game"""
    try:
        view = await async_get_game_control_view_for_game(game)
        if view:
            return await view.update_message()
    except Exception as e:
        log.debug(f"Error when updating associated game listing embed")
    return False
