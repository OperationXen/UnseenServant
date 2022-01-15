import discord
from discord.commands import Option, has_role

from discordbot.bot import bot
from discordbot.components.user_management import BannedPlayerEmbed, BanPlayerView
from core.utils.players import get_outstanding_bans


@bot.slash_command(guild_ids=[691386983670349824], description='Issue a bad conduct strike to a user')
@has_role('admin')
async def strike(ctx, 
    user: Option(discord.Member, 'Member to issue strike against', required=True), 
    reason: Option(str, 'Reason for issuing the strike', required=False)):
    """ Issue a strike against a specified discord user """
    await ctx.respond('pewpew', ephemeral=True, delete_after=15)

@bot.slash_command(guild_ids=[691386983670349824], description='Issue an immediate bot ban to a user')
@has_role('admin')
async def ban(ctx, 
    user: Option(discord.Member, 'Member to ban', required=True), 
    reason: Option(str, 'Reason for issuing this instant ban', required=False)):
    """ Issue a strike against a specified discord user """
    reason = reason if reason else '<Not provided>'
    view = view=BanPlayerView(ctx, user, reason)
    view.message = await ctx.respond(f"Banning player [{user}] for {7} days\nReason: {reason}", view=view)

@has_role('admin')
@bot.slash_command(guild_ids=[691386983670349824], description='Get all currently banned players')
async def bans(ctx):
    """ list all currently banned users """
    embeds = []
    current_bans = await get_outstanding_bans()
    for ban in current_bans:
        embeds.append(BannedPlayerEmbed(ban.discord_name, ban.datetime_end, ban.variant, ban.issued_by, ban.reason))
    if(len(current_bans)):
        await ctx.respond(content=f"{len(current_bans)} players are currently banned from using this service", embeds=embeds)
    else:
        await ctx.respond(content='No players are currently banned')

@has_role('admin')
@bot.slash_command(guild_ids=[691386983670349824], description='Get outstanding strikes and bans')
async def user_standing(ctx,
    user: Option(discord.Member, 'Member to ban', required=True)):
    """ View current strikes and bans for a given user """
    await ctx.respond('pewpew', ephemeral=True, delete_after=15)

@bot.slash_command(guild_ids=[691386983670349824], description='Get your current outstanding strikes and bans')
async def standing(ctx):
    """ Return current user's bans and strikes """
    await ctx.respond('Current ban state...', ephemeral=True, delete_after=15)

