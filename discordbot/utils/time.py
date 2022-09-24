def discord_time(datetime):
    """ Create a discord time (adjusts to local time) """
    return f"<t:{int(datetime.timestamp())}:F>"

def discord_countdown(datetime):
    """ Create a discord time that shows time remaining """
    return f"<t:{int(datetime.timestamp())}:R>"

def discord_date(datetime):
    """ create a discord time that displays as a date string """
    return f"<t:{int(datetime.timestamp())}:D>"

def get_hammertime(datetime):
    """ Wrapper for easy use of schedule info """
    return f"{discord_time(datetime)} ({discord_countdown(datetime)})"
