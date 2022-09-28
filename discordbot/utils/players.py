from discordbot.logs import logger as log
from discordbot.utils.messaging import send_dm
from discordbot.utils.time import discord_countdown

from discordbot.utils.channel import game_channel_tag_promoted_player, game_channel_tag_removed_player
from discordbot.utils.channel import channel_add_player, channel_remove_player, get_channel_for_game
from core.utils.players import populate_game_from_waitlist
from core.utils.games import add_player_to_game, drop_from_game


async def do_waitlist_updates(game):
    """Update a game based on its waitlist"""
    promoted = await populate_game_from_waitlist(game)
    for player in promoted:
        log.info(f"Player {player.discord_name} promoted from waitlist for game {game.name}")
        channel = get_channel_for_game(game)
        channel_add_player(channel, player)
        game_channel_tag_promoted_player(game, player)
        await send_dm(
            player.discord_id,
            f"You have been promoted from the waitlist for {game.name} in {discord_countdown(game.datetime)}!",
        )


async def remove_player_from_game(game, player):
    """Remove a player from a given game"""
    status = await drop_from_game(game, player)
    if status:
        message = f"You have been removed from {game.name}"
    else:
        message = f"You aren't queued for this game..."
    channel = await get_channel_for_game(game)
    await channel_remove_player(channel, player)
    await game_channel_tag_removed_player(game, player)


async def add_player_to_game(game, player):
    pass
