from discord.ext.commands import has_any_role
from discord.commands import Option
from discord import Member, HTTPException, Forbidden

from discordbot.bot import bot
from config.settings import DISCORD_GUILDS, DISCORD_DM_ROLES, DISCORD_ADMIN_ROLES
from discordbot.logs import logger as log
from discordbot.utils.games import update_game_listing_embed
from discordbot.utils.channel import get_game_for_channel, update_mustering_embed
from discordbot.utils.players import remove_player_from_game, do_waitlist_updates
from core.utils.games import get_dm


@bot.command(name="dm_set_name")
async def set_dm_name(ctx, name):
    await ctx.send(f"Set DM alias to {name}")


@bot.command(name="dm_set_bio")
async def set_dm_bio(ctx, *text):
    await ctx.send(f"Set DM biographical text to: \n{' '.join(text)}")


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Force remove a player from a game")
@has_any_role(*DISCORD_DM_ROLES, *DISCORD_ADMIN_ROLES)
async def remove_player(ctx, user: Option(Member, "Member to issue strike against", required=True)):
    """remove a player from a game - should only be run in a game channel"""
    await ctx.response.defer(ephemeral=True)
    log.info(f"{ctx.author.name} used command /remove_player {user.name} in channel {ctx.channel.name}")
    game = await get_game_for_channel(ctx.channel)
    if not game:
        log.error(f"Channel {ctx.channel.name} has no associated game, command failed")
        return await ctx.followup.send("This channel is not linked to a game", ephemeral=True)
    dm = await get_dm(game)
    if dm.discord_id != ctx.author.id:
        log.error(f"{ctx.author.name} does not appear to be the DM for {game.name}, command failed")
        return await ctx.followup.send("You are not the DM for this game", ephemeral=True)

    removed = await remove_player_from_game(game, user)
    if removed:
        await do_waitlist_updates(game)
        await update_mustering_embed(game)
        await update_game_listing_embed(game)
        log.info(f"Removed player {user.name} from game {game.name}")
        try:
            await user.send(f"You were removed from {game.name} on {game.datetime}. Please contact {game.dm.discord_name} if you require more information.")
            log.info(f"{user.name} notified of removal")
        except (HTTPException, Forbidden):
            log.info(f"Exception occured whilst attempting to notify user")

        return await ctx.followup.send("Player removed OK", ephemeral=True)
    log.info(f"Unable to remove player {user.name} from game {game.name}")
    return await ctx.followup.send(f"Unable to remove {user.name} from {game.name}")
