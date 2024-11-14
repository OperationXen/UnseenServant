import random
import re


from discord import Option
from discord.commands import Option

from config.settings import DISCORD_GUILDS
from discord_bot.bot import bot
from discord_bot.logs import logger as log


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Roll an arbitrary number of dice")
async def roll(ctx, dice: Option(str, "Dice to roll (eg 2D10, 8D6)", required=True)):
    """roll an arbitrary number of dice"""
    parsed = re.match("^(\d+)?d(\d+)([\+\-]\d+)?$", dice)
    if not parsed:
        return await ctx.respond(f"Invalid dice roll: `{dice}`", ephemeral=True)
    try:
        num_dice = int(parsed.group(1))
    except (IndexError, TypeError):
        num_dice = 1
    try:
        size_dice = int(parsed.group(2))
    except (IndexError, TypeError):
        size_dice = 20
    try:
        modifier = int(parsed.group(3))
    except (IndexError, TypeError):
        modifier = 0

    rolls = []
    for _roll in range(num_dice):
        result = random.randrange(1, size_dice)
        rolls.append(result)
    total = sum(rolls) + modifier

    log.info(f"[/] User {ctx.author.name} asked me to roll {dice}, result: {rolls}")
    message = f"Rolling `{dice}` for {ctx.author.display_name}: `{str(rolls)}` for a total of `{total}`"
    return await ctx.respond(message, embed=None, ephemeral=False)
