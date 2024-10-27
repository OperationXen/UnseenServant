class ChannelMember:
    """a class to represent existing members in game channels"""

    # member data
    discord_id = ""
    display_name = ""

    # channel data
    channel_id = ""
    channel_name = ""

    # attributes for channel permissions
    read_messages = False
    read_message_history = False
    send_messages = False
    use_slash_commands = False
    manage_messages = False

    def __init__(self, discord_id, display_name, channel_id=None, channel_name="", **kwargs):
        """Instance creation logic"""
        self.discord_id = discord_id
        self.display_name = display_name
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.read_messages = kwargs.get("read_messages")
        self.read_message_history = kwargs.get("read_message_history")
        self.send_messages = kwargs.get("send_messages")
        self.use_slash_commands = kwargs.get("use_slash_commands")
        self.manage_messages = kwargs.get("manage_messages")

    def __str__(self):
        """represent this item as a string"""
        return f"{self.display_name}"
