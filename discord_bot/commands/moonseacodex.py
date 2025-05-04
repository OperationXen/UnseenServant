from discord.commands import Option

from discord_bot.components.moonseacodex.character import MSCCharacterList
from discord_bot.components.moonseacodex.trade import MSCTradeSearchResultsEmbed

from config.settings import DISCORD_GUILDS
from discord_bot.bot import bot
from discord_bot.logs import logger as log
from discord_bot.utils.moonseacodex import get_msc_characters, get_msc_trade_search


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Display a character from the Moonsea Codex")
async def character(ctx):
    """Show a user their moonsea codex characters"""
    await ctx.defer(ephemeral=True)

    log.info(f"[/] {ctx.author.name} used MSC /character command")
    discord_name = str(ctx.author.name)
    characters = get_msc_characters(discord_id=discord_name)
    log.info(f"[-] {len(characters or [])} characters found for {ctx.author.name}")
    if characters:
        view = MSCCharacterList(ctx.author, characters)
        view.message = await ctx.followup.send(
            f"Characters for discord user {discord_name} from the Moonsea Codex:", view=view, ephemeral=True
        )
    else:
        message = await ctx.followup.send(
            f"Cannot find any characters for you on Moonsea Codex, have you set your discord profile ID?"
        )


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Search items for trade on Moonsea Codex")
async def trade_search(ctx, search: Option(str, "Search term to use", required=True)):
    """Query moonsea codex for items available for trading"""
    await ctx.defer(ephemeral=True)
    results_embeds = []

    log.info(f"[/] {ctx.author.name} used MSC /trade_search [{search}] command")
    items = get_msc_trade_search(search)
    num_results = len(items or [])
    log.info(f"[-] {num_results} items found for {ctx.author.name}")
    if not num_results:
        return await ctx.followup.send(f"No matches for '{search}'.", ephemeral=True, delete_after=10)
    else:
        for item in items[:10]:
            embed = MSCTradeSearchResultsEmbed(item)
            results_embeds.append(embed)
        return await ctx.followup.send(
            f"{num_results} Results for '{search}'{', showing first 10:' if num_results > 10 else ':'}",
            embeds=results_embeds,
            ephemeral=True,
        )
