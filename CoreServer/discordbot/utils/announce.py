from config.settings import PRIORITY_CHANNEL_NAME, DEFAULT_CHANNEL_NAME
from discordbot.utils.messaging import get_channel_by_name
from discordbot.components.games import GameControlView, GameDetailEmbed
from core.utils.games import get_current_games

async def announce_game(game, priority):
        """ Build an announcement """
        if priority:
            channel = get_channel_by_name(PRIORITY_CHANNEL_NAME)
        else:
            channel = get_channel_by_name(DEFAULT_CHANNEL_NAME)

        embeds = []
        details_embed = GameDetailEmbed(game)
        await details_embed.build()
        embeds.append(details_embed)

        control_view = GameControlView(game)
        control_view.message = await channel.send(embeds=embeds, view=control_view)

async def repost_all_current_games():
    """ go through the database and repost anything currently accepting signups """
    priority_games = await get_current_games(priority=True)
    for game in priority_games:
        await announce_game(game, priority=True)
    general_games = await get_current_games(priority=False)
    for game in general_games:
        await announce_game(game, priority=False)
