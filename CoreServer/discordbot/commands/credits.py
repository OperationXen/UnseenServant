from django.utils import timezone
from discord.commands import Option, has_any_role
from discord import Member

from config.settings import DISCORD_GUILDS, DISCORD_ADMIN_ROLES
from discordbot.bot import bot
from core.utils.players import get_player_credit_text, issue_player_bonus_credit

from discordbot.utils.time import discord_time


@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Get your current game credit balance')
async def credit(ctx):
    """ Show a user their game credit balance """
    now = timezone.now()
    game_credit_text = await get_player_credit_text(ctx.author)
    message = f"As of: {discord_time(now)}\n{game_credit_text}"

    await ctx.respond(message, ephemeral=True, delete_after=30)

@bot.slash_command(guild_ids=DISCORD_GUILDS, description='Award bonus credits to a given user')
@has_any_role(*DISCORD_ADMIN_ROLES)
async def issue_credit(ctx, 
                    user: Option(Member, 'Member to issue bonus games to', required=True), 
                    reason: Option(str, 'Reason for granting the bonus credits', required=False),
                    credits: Option(int, 'Number of bonus game credits', required=False) = 1,
                    expires_after: Option(int, 'Number of days these credits are valid for (0 or -1 for no expiry)', required=False) = 28):
    """ issue a game credit to a user """
    if expires_after <= 0:
        expires_after = None
    credit_issued = await issue_player_bonus_credit(user, credits, ctx.author, reason or 'Not given', expires_after)
    if credit_issued:
        message = f"{ctx.author.name} has awarded you [{credits}] bonus game credits!"
        if expires_after:
            message = f"{message} These will expire in {expires_after} days"
        else:
            message = f"{message} These do not have a fixed expiry time"
        if reason:
            message = message + f"\nReason given: {reason}"

        pm = await user.send(message)
        await ctx.respond(f"Game credit awarded to {user.name}", ephemeral=True, delete_after=15)
    else:
        await ctx.respond('Failed to issue credit', ephemeral=True, delete_after=15)
