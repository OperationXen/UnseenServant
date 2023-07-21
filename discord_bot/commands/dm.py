from discord.ext.commands import has_any_role
from discord.commands import Option
from discord import Member, HTTPException, Forbidden

from discord_bot.bot import bot
from config.settings import DISCORD_GUILDS, DISCORD_DM_ROLES, DISCORD_ADMIN_ROLES
from discord_bot.logs import logger as log
from core.utils.games import async_get_wait_list
from discord_bot.utils.time import discord_countdown
from discord_bot.utils.games import async_update_game_listing_embed
from discord_bot.utils.channel import get_game_for_channel, update_mustering_embed, notify_game_channel
from discord_bot.utils.players import (
    async_remove_player_from_game,
    async_add_player_to_game,
    async_do_waitlist_updates,
    async_get_party_for_game,
)
from discord_bot.utils.roles import do_dm_permissions_check


@bot.command(name="dm_set_name")
async def set_dm_name(ctx, name):
    await ctx.send(f"Set DM alias to {name}")


@bot.command(name="dm_set_bio")
async def set_dm_bio(ctx, *text):
    await ctx.send(f"Set DM biographical text to: \n{' '.join(text)}")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Force remove a player from a game")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def remove_player(ctx, user: Option(Member, "Player to remove from the game", required=True)):
    """remove a player from a game - should only be run in a game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /remove_player {user.name} in channel {ctx.channel.name}")
    game = await get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    removed = await async_remove_player_from_game(game, user)
    if removed:
        await async_do_waitlist_updates(game)
        await update_mustering_embed(game)
        await async_update_game_listing_embed(game)
        log.info(f"Removed player {user.name} from game {game.name}")
        try:
            await user.send(
                f"You were removed from {game.name} on {game.datetime}. Please contact {game.dm.discord_name} if you require more information."
            )
            log.info(f"{user.name} notified of removal")
        except (HTTPException, Forbidden):
            log.info(f"Exception occured whilst attempting to notify user")

        return await ctx.followup.send("Player removed OK", ephemeral=True)
    log.info(f"Unable to remove player {user.name} from game {game.name}")
    return await ctx.followup.send(f"Unable to remove {user.name} from {game.name}")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Forcibly add a player to a game")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def add_player(ctx, user: Option(Member, "Player to add to the game", required=True)):
    """add a player from a game - should only be run in a game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /add_player {user.name} in channel {ctx.channel.name}")
    game = await get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    added = await async_add_player_to_game(game, user, force=True)
    if added:
        await async_do_waitlist_updates(game)
        await update_mustering_embed(game)
        await async_update_game_listing_embed(game)
        log.info(f"Added player {user.name} to game {game.name}")

        return await ctx.followup.send("Player added to game", ephemeral=True)
    log.info(f"Unable to add player {user.name} to game {game.name}")
    return await ctx.followup.send(f"Unable to add {user.name} to {game.name}")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Tags all players in the party")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def tag_players(ctx):
    """Tags all players in this game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /tag_players in channel {ctx.channel.name}")
    game = await get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    party = await async_get_party_for_game(game)
    message = ""
    for party_member in party:
        discord_user = await bot.fetch_user(party_member.discord_id)
        message += f"{discord_user.mention} "
    await notify_game_channel(game, message)

    log.info(f"Tagged {len(party)} players in channel for game {game.name}")
    return await ctx.followup.send("Party have been individually tagged", ephemeral=True)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Send a warning DM to the player at the top of the waitlist")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def warn_waitlist(ctx):
    """Warns the next player in line"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /warn_waitlist in channel {ctx.channel.name}")
    game = await get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    waitlist = await async_get_wait_list(game)
    try:
        player = waitlist[0]
        discord_user = await bot.fetch_user(player.discord_id)
        await discord_user.send(
            f"You are at the top of the waitlist for **{game.name}** which starts {discord_countdown(game.datetime)}"
        )
        log.debug(f"Player {discord_user.display_name} notified")
        return await ctx.followup.send(f"Player {discord_user.display_name} notified", ephemeral=True)
    except Exception as e:
        log.error(f"Unable to find waitlisted player")
        return await ctx.followup.send("Unable to message player at top of waitlist", ephemeral=True)
