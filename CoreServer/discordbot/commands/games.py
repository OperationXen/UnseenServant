from discord import Embed, Colour

from discordbot.bot import bot
from core.utils.games import get_upcoming_games

from discordbot.components.games import GameDetailEmbed, GameSummaryEmbed, GameControlView


@bot.command(name='games')
async def game_list(ctx, days: int = 30):
    """ show the list of upcoming games (optional days parameter) """
    embeds = []
    upcoming_games = await get_upcoming_games(days)
    embeds.append(Embed(title=f"Games in the next {days} days: [{len(upcoming_games)}]", colour=Colour.dark_purple()))

    for game in upcoming_games:
        summary_embed = GameSummaryEmbed(game)
        await summary_embed.build()
        embeds.append(summary_embed)
    await ctx.send(embeds=embeds)
