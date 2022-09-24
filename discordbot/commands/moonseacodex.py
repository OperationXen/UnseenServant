from discord.commands import Option

from discordbot.components.moonseacodex import MSCCharacterList, MSCTradeSearchResultsEmbed

from config.settings import DISCORD_GUILDS
from discordbot.bot import bot
from discordbot.utils.moonseacodex import get_msc_characters, get_msc_trade_search


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Display a character from the Moonsea Codex")
async def character(ctx):
    """Show a user their moonsea codex characters"""
    await ctx.defer(ephemeral=True)

    characters = get_msc_characters(discord_id=str(ctx.author))
    if characters:
        view = MSCCharacterList(ctx.author, characters)
        view.message = await ctx.followup.send(f"Characters for {ctx.author} from the Moonsea Codex:", view=view, ephemeral=True)
    else:
        message = await ctx.followup.send(f"Cannot find any characters for you on Moonsea Codex, have you set your discord profile ID?")

@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Search items for trade on Moonsea Codex")
async def trade_search(ctx, search: Option(str, 'Search term to use', required=True)):
    """ Query moonsea codex for items available for trading """
    await ctx.defer(ephemeral=True)

    items = get_msc_trade_search(search)

    results_embeds = []
    num_results = len(items)
    if not num_results:
        return await ctx.followup.send(f"No matches for '{search}'.", ephemeral=True)
    else:
        for item in items[:10]:
            embed = MSCTradeSearchResultsEmbed(item)
            results_embeds.append(embed)
        return await ctx.followup.send(f"{num_results} Results for '{search}'{', showing first 10:' if num_results > 10 else ':'}", embeds=results_embeds, ephemeral=True)
