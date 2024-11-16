from config.settings import DISCORD_GUILDS
from discord_bot.bot import bot
from discord_bot.logs import logger as log

from discord_bot.components.bastion import BastionEmbed


@bot.slash_command(guild_ids=DISCORD_GUILDS, description="Automates a bastion turn")
async def bastion(ctx):
    await ctx.response.defer(ephemeral=False)

    log.info(f"[/] {ctx.author.name} used command /bastion in channel {ctx.channel.name}")

    embed = BastionEmbed(ctx.author.display_name)
    await ctx.followup.send(f"", embed=embed)
