import discord
from discord.commands import Option, has_role

from discordbot.bot import bot
from discordbot.components.user_management import PlayerBanEmbed, PlayerStrikeEmbed, BanPlayerView
from core.utils.players import get_outstanding_bans
from core.utils.strikes import issue_player_strike, get_outstanding_strikes


@bot.slash_command(guild_ids=[691386983670349824], description='Issue a bad conduct strike to a user')
@has_role('admin')
async def strike(ctx, 
    user: Option(discord.Member, 'Member to issue strike against', required=True), 
    reason: Option(str, 'Reason for issuing the strike', required=False)):
    """ Issue a strike against a specified discord user """
    reason = reason if reason else '<Not provided>'
    ban_issued = await issue_player_strike(user, reason, ctx.author)
    if ban_issued:
        await ctx.respond('Strike threshold reached, user has been banned', ephemeral=True, delete_after=15)
    else:
        await ctx.respond(f"Strike issued to {user.name}", ephemeral=True, delete_after=15)

@bot.slash_command(guild_ids=[691386983670349824], description='Issue an immediate bot ban to a user')
@has_role('admin')
async def ban(ctx, 
    user: Option(discord.Member, 'Member to ban', required=True), 
    reason: Option(str, 'Reason for issuing this instant ban', required=False)):
    """ Issue an immediate ban to a specified discord user """
    reason = reason if reason else '<Not provided>'
    view = BanPlayerView(ctx, user, reason)
    view.message = await ctx.respond(f"Banning player [{user}] for {7} days\nReason: {reason}", view=view, ephemeral=True)

@bot.slash_command(guild_ids=[691386983670349824], description='Get all currently banned players')
@has_role('admin')
async def bans(ctx):
    """ list all currently banned users """
    embeds = []
    current_bans = await get_outstanding_bans()
    for ban in current_bans:
        embeds.append(PlayerBanEmbed(ban))
    if(len(current_bans)):
        await ctx.respond(content=f"{len(current_bans)} players are currently banned from using this service", embeds=embeds, ephemeral=True)
    else:
        await ctx.respond(content='No users are currently banned', ephemeral=True)

@bot.slash_command(guild_ids=[691386983670349824], description='Get outstanding strikes and bans for a specified user')
@has_role('admin')
async def user_standing(ctx,
    user: Option(discord.Member, 'Member to ban', required=True)):
    """ View current strikes and bans for a given user """
    embeds = []
    strikes = await get_outstanding_strikes(user)
    for strike in strikes:
        embeds.append(PlayerStrikeEmbed(strike))
    bans = await get_outstanding_bans(user)
    for ban in bans:
        embeds.append(PlayerBanEmbed(ban))
    if not strikes and not bans:
        await ctx.respond(f"User {user.name} is in good standing", ephemeral=True, delete_after=15)
    elif bans:
        await ctx.respond(f"User {user.name} is currently serving a ban", embeds=embeds, ephemeral=True, delete_after=15)
    else:
        await ctx.respond('Outstanding warnings', embeds=embeds, ephemeral=True, delete_after=15)

@bot.slash_command(guild_ids=[691386983670349824], description='Get your current outstanding strikes and bans')
async def standing(ctx):
    """ Return current user's bans and strikes """
    embeds = []
    strikes = await get_outstanding_strikes(ctx.author)
    for strike in strikes:
        embeds.append(PlayerStrikeEmbed(strike))
    bans = await get_outstanding_bans(ctx.author)
    for ban in bans:
        embeds.append(PlayerBanEmbed(ban))
    if not strikes and not bans:
        await ctx.respond('You are in good standing with no strikes or bans', ephemeral=True, delete_after=15)
    else:
        await ctx.respond('Your outstanding bans and warnings', embeds=embeds, ephemeral=True, delete_after=15)
