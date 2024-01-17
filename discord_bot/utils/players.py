from discord_bot.logs import logger as log
from discord_bot.utils.messaging import async_send_dm
from discord_bot.utils.time import discord_countdown
from core.utils.games import check_game_pending, async_get_player_list, async_get_wait_list

from discord_bot.utils.channel import (
    async_game_channel_tag_promoted_user,
    async_game_channel_tag_removed_user,
    async_game_channel_tag_promoted_player,
)
from discord_bot.utils.channel import (
    async_channel_add_player,
    async_channel_remove_user,
    async_get_channel_for_game,
)
from core.utils.players import async_populate_game_from_waitlist
from core.utils.games import (
    async_db_add_player_to_game,
    async_db_force_add_player_to_game,
    async_db_remove_discord_user_from_game,
)


async def async_do_waitlist_updates(game):
    """Update a game based on its waitlist"""
    promoted = await async_populate_game_from_waitlist(game)
    game_outstanding = check_game_pending(game)
    for player in promoted:
        log.info(f"Player {player.discord_name} promoted from waitlist for game {game.name}")
        channel = await async_get_channel_for_game(game)

        await async_channel_add_player(channel, player)
        # Only ping players if they're being promoted into a game that hasn't started
        if game_outstanding:
            await async_game_channel_tag_promoted_player(game, player)
            await async_send_dm(
                player.discord_id,
                f"You have been promoted from the waitlist for {game.name} {discord_countdown(game.datetime)}!",
            )


async def async_remove_player_from_game(game, discord_user):
    """Remove a player from a given game"""
    removed_from_party = await async_db_remove_discord_user_from_game(game, str(discord_user.id))
    if removed_from_party is None:
        return False
    elif removed_from_party:
        channel = await async_get_channel_for_game(game)
        if channel:
            await async_channel_remove_user(channel, discord_user)
            await async_game_channel_tag_removed_user(game, discord_user)
    return True


async def async_add_player_to_game(game, discord_user, force=False):
    """Add a discord user to a game"""
    if force:
        player = await async_db_force_add_player_to_game(game, discord_user)
    else:
        player = await async_db_add_player_to_game(game, discord_user)
    if player and not player.standby:
        channel = await async_get_channel_for_game(game)
        if channel:
            await async_channel_add_player(channel, discord_user)
            await async_game_channel_tag_promoted_user(game, discord_user)
    return player


async def async_get_party_for_game(game, include_waitlist=False):
    """Get a list of all players who are part of the game's party"""
    party = await async_get_player_list(game)
    if include_waitlist:
        try:
            waitlist = await async_get_wait_list(game)
            party.append(waitlist[0])
        except Exception as e:
            pass
    return party
