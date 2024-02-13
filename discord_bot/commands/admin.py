import discord
from discord.commands import Option
from discord.ext.commands import has_any_role
from django.db import IntegrityError
from django.forms import ValidationError

import discord_bot.core
from discord_bot.bot import bot
from discord_bot.components.admin import AdminUserCreatedEmbed
from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES, DISCORD_DM_ROLES
from core.utils.admin import async_create_new_dm_from_discord_user, async_create_new_admin_user
from discord_bot.utils.roles import async_set_user_dm_registered


@bot.slash_command(
    guild_ids=DISCORD_GUILDS, description="Resummon the Unseen Servant - rebuilding posts from the arcane store"
)
@has_any_role(*DISCORD_ADMIN_ROLES)
async def resummon(ctx):
    """Force the bot to rebuild its internal state"""
    discord_bot.core.game_controller.initialised = False
    await ctx.respond(
        f"Redraw the summoning circle and light the candles - the Unseen Servant is invoked",
        ephemeral=True,
        delete_after=10,
    )
