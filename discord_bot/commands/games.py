from django.utils import timezone
from discord import Embed, Colour, Option

from config.settings import DISCORD_GUILDS
from discord_bot.bot import bot
from discord_bot.logs import logger as log
from core.utils.games import (
    async_get_upcoming_games,
    async_get_upcoming_games_for_dm_discord_id,
    async_get_upcoming_games_for_discord_id,
)
from core.utils.players import async_get_player_credit_text

from discord_bot.components.games import GameSummaryEmbed
from discord_bot.utils.time import discord_time


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Summary of your upcoming games (both playing and DMing)")
async def games(ctx, send_dm: Option(bool, "Send information in a DM instead of inline", required=False) = False):
    """Retrieve a list of the users upcoming games and provide a summary"""
    now = timezone.now()
    game_credit_text = await async_get_player_credit_text(ctx.author)
    games = await async_get_upcoming_games_for_discord_id(ctx.author.id, waitlisted=False)
    waitlist = await async_get_upcoming_games_for_discord_id(ctx.author.id, waitlisted=True)
    dming = await async_get_upcoming_games_for_dm_discord_id(ctx.author.id)

    log.debug(
        f"Command: [/games] used by User [{ctx.author.name}], PM requested [{send_dm}], DMing [{len(dming)}], Playing [{len(games)}], Waitlist [{len(waitlist)}]"
    )

    if send_dm:
        await ctx.author.send(f"As of: {discord_time(now)}\n{game_credit_text}")
        await ctx.respond(f"Please check your PMs", ephemeral=True, delete_after=15)
    else:
        await ctx.respond(f"As of: {discord_time(now)}\n{game_credit_text}", ephemeral=True)

    if dming:
        embeds = []
        for game in dming[:10]:
            summary_embed = GameSummaryEmbed(game, colour=Colour.blue())
            await summary_embed.build()
            embeds.append(summary_embed)
        message = f"You are DMing {len(dming)} games"
        if send_dm:
            await ctx.author.send(message, embeds=embeds)
        else:
            await ctx.respond(message, embeds=embeds, ephemeral=True)

    if games:
        embeds = []
        for game in games[:10]:
            summary_embed = GameSummaryEmbed(game, colour=Colour.dark_purple())
            await summary_embed.build()
            embeds.append(summary_embed)
        message = f"You are registered for {len(games)} games"
        if send_dm:
            await ctx.author.send(message, embeds=embeds)
        else:
            await ctx.respond(message, embeds=embeds, ephemeral=True)

    if waitlist:
        embeds = []
        for game in waitlist[:10]:
            summary_embed = GameSummaryEmbed(game, colour=Colour.dark_green())
            await summary_embed.build()
            embeds.append(summary_embed)
        message = f"You are waitlisted for {len(waitlist)} games"
        if send_dm:
            await ctx.author.send(message, embeds=embeds)
        else:
            await ctx.respond(message, embeds=embeds, ephemeral=True)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="All upcoming games within a time period (default is 30 days)")
async def games_summary(ctx, days: Option(int, "Number of days", required=False) = 30):
    """Find all upcoming games for the next N days and list them as a summary print"""
    embeds = []
    await ctx.response.defer(ephemeral=True)
    upcoming_games = await async_get_upcoming_games(days)
    embeds.append(Embed(title=f"Games in the next {days} days: [{len(upcoming_games)}]", colour=Colour.dark_purple()))

    for game in upcoming_games[0:9]:
        summary_embed = GameSummaryEmbed(game)
        await summary_embed.build()
        embeds.append(summary_embed)
    await ctx.respond(embeds=embeds, ephemeral=True)
