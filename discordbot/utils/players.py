from discordbot.logs import logger as log
from discordbot.utils.channel import notify_game_channel
from discordbot.utils.messaging import send_dm
from discordbot.utils.time import discord_countdown

from discordbot.utils.channel import game_channel_tag_promoted_player, game_channel_tag_removed_player
from discordbot.utils.channel import game_channel_add_player, game_channel_remove_player
from core.utils.players import populate_game_from_waitlist
from core.utils.games import drop_from_game


async def do_waitlist_updates(game):
    """ Update a game based on its waitlist """
    promoted = await populate_game_from_waitlist(game)
    for player in promoted:
        log.info(f"Player {player.discord_name} promoted from waitlist for game {game.name}")
        game_channel_add_player(game, player)
        game_channel_tag_promoted_player(game, player)
        await send_dm(player.discord_id, f"You have been promoted from the waitlist for {game.name} in {discord_countdown(game.datetime)}!")

async def remove_player_from_game(game, player):
    """ Remove a player from a given game """    
    status = await drop_from_game(game, player)
    if status:
        message = f"You have been removed from {game.name}"
    else:
        message = f"You aren't queued for this game..."
    game_channel_remove_player(game, player)
    game_channel_tag_removed_player(game, player)
    