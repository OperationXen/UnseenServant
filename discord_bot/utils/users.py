from discord_bot.bot import bot


async def async_get_username_for_discord_id(discord_id: str) -> str | None:
    try:
        user = bot.get_user(discord_id)
        if user:
            return user.name
        user = await bot.fetch_user(discord_id)
        if user:
            return user.name
    except Exception as e:
        print(e)
    return None
