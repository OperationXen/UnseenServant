from discordbot.bot import bot

@bot.command(name='dm_set_name')
async def set_dm_name(ctx, name):
    await ctx.send(f"Set DM alias to {name}")

@bot.command(name='dm_set_bio')
async def set_dm_bio(ctx, *text):
    await ctx.send(f"Set DM biographical text to: \n{' '.join(text)}")
