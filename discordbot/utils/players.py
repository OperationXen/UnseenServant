from discordbot.logs import logger as log
from discordbot.utils.messaging import send_dm
from discordbot.utils.time import discord_countdown

from discordbot.utils.channel import game_channel_tag_promoted_user, game_channel_tag_removed_user, game_channel_tag_promoted_player
from discordbot.utils.channel import channel_add_player, channel_add_user, channel_remove_user, get_channel_for_game
from core.utils.players import populate_game_from_waitlist
from core.utils.games import db_add_player_to_game, db_remove_discord_user_from_game


async def do_waitlist_updates(game):
    """Update a game based on its waitlist"""
    promoted = await populate_game_from_waitlist(game)
    for player in promoted:
        log.info(f"Player {player.discord_name} promoted from waitlist for game {game.name}")
        channel = await get_channel_for_game(game)

        await channel_add_player(channel, player)
        await game_channel_tag_promoted_player(game, player)
        await send_dm(
            player.discord_id,
            f"```You have been promoted from the waitlist for {game.name} in {discord_countdown(game.datetime)}!```",
        )


async def remove_player_from_game(game, discord_user):
    """Remove a player from a given game"""
    removed = await db_remove_discord_user_from_game(game, discord_user)
    if removed:
        channel = await get_channel_for_game(game)
        if channel:
            await channel_remove_user(channel, discord_user)
            await game_channel_tag_removed_user(game, discord_user)
        return True
    return False


async def add_player_to_game(game, discord_user):
    """ Add a discord user to a game"""
    added = await db_add_player_to_game(game, discord_user)
    if added == 'party':
        channel = await get_channel_for_game(game)
        if channel:
            await channel_add_user(channel, discord_user)
            await game_channel_tag_promoted_user(game, discord_user)
    return added
