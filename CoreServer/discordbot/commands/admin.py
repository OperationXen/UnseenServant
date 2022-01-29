import discord
from discord.commands import Option, has_any_role
from django.db import IntegrityError
from django.forms import ValidationError

from discordbot.bot import bot
from discordbot.components.admin import AdminUserCreatedEmbed
from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from core.utils.admin import create_new_dm_from_discord_user, create_new_admin_user

@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Register a new DM account')
@has_any_role(*DISCORD_ADMIN_ROLES)
async def register_as_dm(ctx, 
        user: Option(discord.Member, 'Discord Member to register', required=False) = None, 
        name: Option(str, 'The DM\'s display name (if different to their discord name', required=False) = None,  
        description: Option(str, 'A brief blurb about you and your Dungeoneering preferences', required=False) = None):
    """ Registers the user as a DM and creates them an admin page user """
    user = user if user else ctx.user
    try:
        await create_new_dm_from_discord_user(user, name, description)
        username, password = await create_new_admin_user(name or user.name)
    except (ValidationError, IntegrityError):
        await ctx.respond(f"Failed to create new Dungeon Master, are you already registered?", ephemeral=True, delete_after=10)
        return

    await user.send(f"", embed = AdminUserCreatedEmbed(username=username, password = password))
    await ctx.respond(f"Registration successful, information PMed to user", ephemeral=True, delete_after=10)
