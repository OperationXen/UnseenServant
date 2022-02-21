from discordbot.utils.messaging import send_dm
from discordbot.utils.time import discord_countdown
from core.utils.players import populate_game_from_waitlist


async def do_waitlist_updates(game):
    """ Update a game based on its waitlist """
    promoted = await populate_game_from_waitlist(game)
    for player in promoted:
        await send_dm(player.discord_id, f"You have been promoted from the waitlist for {game.name} in {discord_countdown(game.datetime)}!")
