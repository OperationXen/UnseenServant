from discord.ext.commands import has_any_role
from discord.commands import Option
from discord import Member

from config.settings import DISCORD_GUILDS, DISCORD_DM_ROLES, DISCORD_ADMIN_ROLES
from discord_bot.bot import bot
from discord_bot.logs import logger as log
from core.utils.games import async_get_wait_list
from core.utils.channels import async_get_game_channel_for_game
from core.utils.players import async_get_user_from_player
from core.errors import ChannelError
from discord_bot.utils.time import discord_countdown
from discord_bot.utils.messaging import async_send_dm
from discord_bot.utils.embed import async_update_game_embeds
from discord_bot.utils.channel import async_remove_discord_member_from_game_channel

from discord_bot.utils.channel import (
    async_get_game_for_channel,
    async_notify_game_channel,
)
from discord_bot.utils.players import (
    async_do_waitlist_updates,
    async_get_party_for_game,
)
from discord_bot.utils.games import async_add_discord_member_to_game, async_remove_discord_member_from_game
from discord_bot.utils.roles import do_dm_permissions_check


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Force remove a player from a game")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def remove_player(ctx, user: Option(Member, "Player to remove from the game", required=True)):
    """remove a player from a game - should only be run in a game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"[/] {ctx.author.name} used command /remove_player {user.name} in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"[!] Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True, delete_after=10)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True, delete_after=10)

    removed = await async_remove_discord_member_from_game(user, game)
    if removed:
        try:
            game_channel = await async_get_game_channel_for_game(game)
        except ChannelError:
            log.error(f"[!] Unable to find a GameChannel object for game: {game.name}")
            return await ctx.followup.send("GameChannel object missing in db", ephemeral=True, delete_after=10)
        await async_remove_discord_member_from_game_channel(user, game_channel)
        await async_do_waitlist_updates(game)
        await async_update_game_embeds(game)
        log.info(f"[.] Removed player {user.name} from game {game.name}")

        message = f"You were removed from {game.name} on {game.datetime}. Please contact {ctx.author.name} if you require more information."
        if await async_send_dm(user, message):
            log.info(f"[.] {user.name} notified of removal")
        else:
            log.warning(f"[!] could not notify {user.name} of removal")

        return await ctx.followup.send("Player removed OK", ephemeral=True, delete_after=10)
    log.info(f"[.] Unable to remove player {user.name} from game {game.name}")
    return await ctx.followup.send(f"Unable to remove {user.name} from {game.name}", ephemeral=True, delete_after=10)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Forcibly add a player to a game")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def add_player(ctx, user: Option(Member, "Player to add to the game", required=True)):
    """add a player to a game - should only be run in a game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"[-] {ctx.author.name} used command /add_player {user.name} in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"[!] Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True, delete_after=10)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True, delete_after=10)

    added = await async_add_discord_member_to_game(user, game, force=True)
    if added:
        await async_do_waitlist_updates(game)
        await async_update_game_embeds(game)
        message = f"{ctx.author.name} added you to game {game.name}"
        await async_send_dm(user, message)

        log.info(f"[-] Added player {user.name} to game {game.name}")
        return await ctx.followup.send("Player added to game", ephemeral=True, delete_after=10)
    log.info(f"[-] Unable to add player {user.name} to game {game.name}")
    return await ctx.followup.send(f"Unable to add {user.name} to {game.name}", ephemeral=True, delete_after=10)


# ##################################################################################################### #


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Forcibly add a player to a game waitlist")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def add_waitlist(ctx, user: Option(Member, "Player to add to the waitlist", required=True)):
    """add a player to a games waitlist - should only be run in a game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"[/] {ctx.author.name} used command /add_waitlist {user.name} in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"[!] Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True, delete_after=10)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True, delete_after=10)

    added = await async_add_discord_member_to_game(user, game, force=False)
    if added:
        await async_do_waitlist_updates(game)
        await async_update_game_embeds(game)

        if added.waitlist:
            log.info(f"[-] Added {user.name} to game {game.name} waitlist")
            message = "Player added to waitlist"
            await async_send_dm(user, f"{ctx.author.name} added you to the waitlist for {game.name}")
        else:
            log.info(f"[-] Added {user.name} to game {game.name}")
            message = "Player added to game, as there was a space"
            await async_send_dm(user, f"{ctx.author.name} added you to game {game.name}")
        return await ctx.followup.send(message, ephemeral=True, delete_after=10)
    log.info(f"[-] Unable to add player {user.name} to waitlist {game.name}")
    return await ctx.followup.send(f"Unable to add {user.name} to waitlist for {game.name}", delete_after=10)


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Tags all players in the party")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def tag_players(ctx):
    """Tags all players in this game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /tag_players in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    party = await async_get_party_for_game(game)
    message = "Attention players: "
    for party_member in party:
        user = await async_get_user_from_player(party_member)
        try:
            discord_user = await bot.fetch_user(user.discord_id)
            message += f"{discord_user.mention} "
        except Exception as e:
            pass
    await async_notify_game_channel(game, message)

    log.info(f"Tagged {len(party)} players in channel for game {game.name}")
    return await ctx.followup.send("Party have been individually tagged", ephemeral=True, delete_after=10)


@bot.slash_command(
    guild_ids=DISCORD_GUILDS,
    description="Send a warning DM to the player at the top of the waitlist",
)
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def warn_waitlist(ctx):
    """Warns the next player in line"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /warn_waitlist in channel {ctx.channel.name}")
    game = await async_get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)

    if not do_dm_permissions_check(ctx.author, game):
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    waitlist = await async_get_wait_list(game)
    try:
        player = waitlist[0]
        discord_user = await bot.fetch_user(player.discord_id)

        message = f"You are at the top of the waitlist for **{game.name}**"
        message += f" which starts {discord_countdown(game.datetime)}"
        if await async_send_dm(discord_user, message):
            return await ctx.followup.send(f"Player {discord_user.display_name} notified", ephemeral=True)
        else:
            return await ctx.followup.send("Unable to message player at top of waitlist", ephemeral=True)
    except Exception as e:
        log.error(f"[!] Unable to find waitlisted player: {e}")
        return await ctx.followup.send("Something went wrong whilst warning the waitlist...", ephemeral=True)
