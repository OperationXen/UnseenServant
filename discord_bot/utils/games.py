import re

from discord_bot.logs import logger as log
from discord_bot.bot import bot
from discord import Member as DiscordMember
from discord.ui import Button

from core.utils.games import async_get_game_by_id
from core.utils.games_rework import add_user_to_game, remove_user_from_game
from core.utils.user import get_user_by_discord_id
from core.models import Game, Player

from discord_bot.utils.auth import create_user_from_discord_member


def is_button(element):
    return type(element) is Button


def get_game_number(input):
    """Retrieve a game number from a string"""
    result = re.search("(\d+)", input)
    if result:
        return int(result.group(1))
    return None


def get_game_id_from_message(message) -> int | None:
    """Given a generic message, attempt to get the game ID it refers"""
    for row in message.components:
        for button in filter(lambda x: is_button, row.children):
            if not button.custom_id:
                continue
            game_id = get_game_number(button.custom_id)
            if game_id:
                return game_id
    return None


async def async_get_game_from_message(message) -> Game | None:
    """Given a generic message, attempt to get the game instance it refers to [if any]"""
    try:
        game_id = get_game_id_from_message(message)
        if game_id:
            game = await async_get_game_by_id(game_id)
            return game
    except Exception as e:
        log.error(e)
    return None


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


# ################################################################################ #
def add_discord_member_to_game(member: DiscordMember, game: Game, force: bool = False) -> Player | None:
    """2024 Rework - Wrapper to facilitate adding a member/user to a game by their discord id"""
    user = get_user_by_discord_id(member.id)
    if not user:
        try:
            user = create_user_from_discord_member(member)
        except Exception as e:
            return None
    return add_user_to_game(user, game, force)


async def async_add_discord_member_to_game(member: DiscordMember, game: Game, force: bool = False) -> Player | None:
    """Async wrapper to allow this utility to be called from an async context"""
    player = add_discord_member_to_game(member, game, force)
    return player


def remove_discord_member_from_game(member: DiscordMember, game: Game) -> bool:
    """Remove a discord member from a game"""
    user = get_user_by_discord_id(member.id)
    if not user:
        return False
    return remove_user_from_game(user, game)


async def async_remove_discord_member_from_game(member: DiscordMember, game: Game) -> bool:
    """Async wrapper for removing a discord member from game"""
    success = remove_discord_member_from_game
    return success
