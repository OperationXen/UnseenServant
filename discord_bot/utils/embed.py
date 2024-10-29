from asyncio import gather, create_task
from enum import Enum

from discord_bot.bot import bot
from discord_bot.logs import logger as log
from core.models import Game


# ######################### Utility function ################################### #
class ViewType(Enum):
    MUSTERING = 1
    CONTROL = 2


def get_view_for_game(game: Game, view_type: ViewType):
    """Get the view for a game from the bot's connected views"""
    for view in bot.persistent_views:
        view_name = str(type(view))
        if view_type is ViewType.MUSTERING and "MusteringView" in view_name and view.game == game:
            return view
        if view_type is ViewType.CONTROL and "GameControlView" in view_name and view.game == game:
            return view
    return None


# ######################### Mustering Embeds ################################### #
async def async_update_mustering_embed(game: Game):
    """Refresh a mustering embed for a specific game"""
    try:
        view = get_view_for_game(game, ViewType.MUSTERING)
        if view:
            return await view.update_message()
    except Exception as e:
        log.error(f"[!] Error when updating associated muster embed: {e}")
    return False


# ######################### Game Channel Embeds ################################### #
async def async_update_game_listing_embed(game: Game):
    """Refresh a game listing embed for a specific game"""
    try:
        view = get_view_for_game(game, ViewType.CONTROL)
        if view:
            return await view.update_message()
    except Exception as e:
        log.error(f"[!] Error when updating associated game listing embed: {e}")
    return False


# ######################### Higher order functions ################################### #
async def async_update_game_embeds(game: Game):
    """Update all embeds for the specified game"""
    pending = []
    try:
        pending.append(create_task(async_update_mustering_embed(game)))
        pending.append(create_task(async_update_game_listing_embed(game)))
        await gather(*pending)
    except Exception as e:
        log.error(f"[!] Error in embed update: {e}")
        return False
    return True
