from discord import SelectOption
from discord.commands import Option

from discordbot.components.moonseacodex import MSCCharacterList
from discordbot.utils.moonseacodex import get_character_string

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES, DISCORD_SIGNUP_ROLES, DISCORD_DM_ROLES
from discordbot.bot import bot
from discordbot.utils.moonseacodex import get_msc_characters
from core.utils.players import get_player_credit_text, issue_player_bonus_credit



@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Display a character from the Moonsea Codex")
async def character(ctx):
    """Show a user their moonsea codex characters"""
    await ctx.defer(ephemeral=True)

    characters = get_msc_characters(discord_id=str(ctx.author))
    if characters:
        view = MSCCharacterList(ctx, characters)
        view.message = await ctx.followup.send(f"Characters for {ctx.author} from the Moonsea Codex:", view=view, ephemeral=True)
    else:
        message = await ctx.followup.send(f"Cannot find any characters for you on Moonsea Codex, have you set your discord profile ID?")
