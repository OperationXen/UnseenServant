from discord.ext.commands import has_any_role


from discord_bot.bot import bot
from config.settings import DISCORD_GUILDS, DISCORD_DM_ROLES, DISCORD_ADMIN_ROLES
from discord_bot.logs import logger as log
from discord_bot.utils.roles import do_dm_permissions_check
from discord_bot.utils.channel import (
    async_get_game_for_channel,
    async_remove_all_channel_members,
    async_add_channel_users,
)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Resets channel membership")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def reset_channel_membership(ctx):
    """Resets membership of a given game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /reset_channel_membership in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    try:
        await async_remove_all_channel_members(ctx.channel)
        log.info(f"Channel membership cleared, re-adding users")
        await async_add_channel_users(ctx.channel, game)
        log.info(f"Channel members re-added, reset complete")
        return await ctx.followup.send(f"Channel membership reset", ephemeral=True)
    except Exception as e:
        return await ctx.followup.send(
            "A problem occured whilst attempting to reset channel membership", ephemeral=True
        )
