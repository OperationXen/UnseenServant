from discord_bot.bot import bot


def add_persistent_view(view):
    """Register a persistent view with the bot"""
    bot.add_view(view)
