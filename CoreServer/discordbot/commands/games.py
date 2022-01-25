from django.utils import timezone
from discord import Embed, Colour
from discord.commands import Option, has_any_role

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from discordbot.bot import bot
from core.utils.games import get_upcoming_games, get_upcoming_games_for_player, get_upcoming_games_for_dm

from discordbot.components.banners import DMSummaryBanner, GameSummaryBanner, WaitlistSummaryBanner
from discordbot.components.games import GameDetailEmbed, GameSummaryEmbed, GameControlView
from discordbot.utils.time import discord_time


@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Summary of your upcoming games (both playing and DMing)')
async def games(ctx, send_dm: Option(bool, 'Send information in a DM instead of inline', required=False) = False):
    """ Retrieve a list of the users upcoming games and provide a summary """
    now = timezone.now()
    message = f"As of: {discord_time(now)}"
    embeds = []
    games = await get_upcoming_games_for_player(ctx.author.id, waitlisted=False)
    dming = await get_upcoming_games_for_dm(ctx.author.id)

    if dming:
        embeds.append(DMSummaryBanner(games=len(dming)))
        for game in dming:
            summary_embed = GameSummaryEmbed(game, colour=Colour.red())
            await summary_embed.build()
            embeds.append(summary_embed)

    if games:
        for game in games:
            summary_embed = GameSummaryEmbed(game, colour=Colour.green())
            await summary_embed.build()
            embeds.append(summary_embed)
    if send_dm:
        await ctx.author.send(message, embeds=embeds)
        await ctx.respond("DM Sent!", delete_after=3)
    else:
        await ctx.respond(message, ephemeral=True, embeds=embeds)

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
    await ctx.respond(embeds=embeds, ephemeral=True)
