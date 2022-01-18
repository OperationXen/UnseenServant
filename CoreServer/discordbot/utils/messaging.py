from discordbot.bot import bot

async def send_dm(discord_id, message):
    user = await bot.get_or_fetch_user(discord_id)
    print("User")

def get_channel_by_name(channel_name):
    """ Attempt to retieve a channel by a name """
    for channel in bot.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None

async def get_guild_channel(channel_name):
    asdfsadf # TODO - this needs fixing
    """ retrieve a specific named channel for a given guild """
    for channel in bot.guild.channels:
        if channel.name == channel_name:
            return channel

async def send_channel_message(message, channel = None):
    """ Send a message to a channel """
    if type(channel) == str:
        channel = get_channel_by_name('bot-test-channel')
    elif type(channel) == int:
        channel = bot.get_channel(channel)

    if channel:
        await channel.send(**message)

def message_should_be_purged(m):
    """ Helper function to determine if a message should be removed or not """
    if m.author == bot.user:
        return True
    if m.content and m.content[0] == '!':
        return True
    return False

async def remove_existing_messages(channels):
    """ Find and remove all previously posted bot messages - not the cleanest solution, but a first pass """
    for channel in bot.get_all_channels():
        if channel.name in channels:
            await channel.purge(check=message_should_be_purged, limit=5000)

async def get_bot_game_postings(channel):
    """ Retrieve a list of message objects posted by this bot in this channel """
    messages = await channel.history().flatten()
    messages = filter(lambda message: message.author == bot.user, messages)
    return list(messages)