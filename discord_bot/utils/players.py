from discord_bot.logs import logger as log
from discord_bot.utils.messaging import async_send_dm
from discord_bot.utils.time import discord_countdown
from core.utils.games import check_game_pending, async_get_player_list, async_get_wait_list

from discord_bot.utils.channel import async_get_game_channel_for_game
from core.utils.players import async_populate_game_from_waitlist, async_get_user_from_player
from core.utils.channel_members import async_add_user_to_game_channel
from core.errors import ChannelError

from discord_bot.logs import logger as log


async def async_do_waitlist_updates(game):
    """Update a game based on its waitlist"""
    promoted = await async_populate_game_from_waitlist(game)
    game_outstanding = check_game_pending(game)
    for player in promoted:
        user = await async_get_user_from_player(player)
        log.info(f"[>] User {user.discord_name} promoted from waitlist for game {game.name}")
        try:
            game_channel = await async_get_game_channel_for_game(game)
            await async_add_user_to_game_channel(user, game_channel)
        except ChannelError:
            pass  # no existing game channel, this is fine
        except Exception as e:
            log.error(f"[!] Exception adding promoted user {user.discord_name} to channel for game {game.name}")
        # Only ping players if they're being promoted into a game that hasn't started
        if game_outstanding:
            message = f"You have been promoted from the waitlist for {game.name} {discord_countdown(game.datetime)}!"
            await async_send_dm(user.discord_id, message)


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
