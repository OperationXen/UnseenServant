from discord import Embed, Colour
from discord.commands import Option, has_any_role

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from discordbot.bot import bot
from core.utils.games import get_upcoming_games, get_upcoming_games_for_user, get_upcoming_games_for_dm

from discordbot.components.games import GameDetailEmbed, GameSummaryEmbed, GameControlView


@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Summary of your upcoming games (both playing and DMing')
async def games(ctx):
    """ Retrieve a list of the users upcoming games and provide a summary """
    games = get_upcoming_games_for_user(ctx.author)
    dming = get_upcoming_games_for_dm(ctx.author)

    await ctx.respond(f"Upcoming games", ephemeral=True, delete_after=60.0)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description='All upcoming games within a time period (default is 30 days)')
@has_any_role(*DISCORD_ADMIN_ROLES)
async def games_summary(ctx, days: Option(int, 'Number of days', required=False) = 30): 
    """ Find all upcoming games for the next N days and list them as a summary print """
    embeds = []
    upcoming_games = await get_upcoming_games(days)
    embeds.append(Embed(title=f"Games in the next {days} days: [{len(upcoming_games)}]", colour=Colour.dark_purple()))

    for game in upcoming_games:
        summary_embed = GameSummaryEmbed(game)
        await summary_embed.build()
        embeds.append(summary_embed)
    await ctx.send(embeds=embeds)
