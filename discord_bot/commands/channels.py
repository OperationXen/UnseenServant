from discord.ext.commands import has_any_role

from discord_bot.bot import bot
from config.settings import DISCORD_GUILDS, DISCORD_DM_ROLES, DISCORD_ADMIN_ROLES
from discord_bot.logs import logger as log
from discord_bot.utils.roles import do_dm_permissions_check
from discord_bot.utils.channel import async_get_game_for_channel
from core.utils.channels import async_set_default_channel_membership
from core.utils.channels import async_get_game_channel_for_game


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Resets channel membership")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def reset_channel_membership(ctx):
    """Resets membership of a given game channel"""
    await ctx.response.defer(ephemeral=True, invisible=True)
    log.info(f"[/] {ctx.author.name} used command /reset_channel_membership in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"[!] Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    game_channel = await async_get_game_channel_for_game(game)
    set_members = await async_set_default_channel_membership(game_channel)
    if set_members:
        log.info(f"[-] Channel membership reset to default")
        return await ctx.followup.send("Channel membership reset", ephemeral=True, delete_after=10)
    else:
        log.error(f"[!] Failed to reset channel membership to defaults")
        return await ctx.followup.send("Unable to perform channel membership reset", ephemeral=True, delete_after=10)
