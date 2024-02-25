from datetime import datetime as dt, timedelta


def discord_time(datetime: dt):
    """Create a discord time (adjusts to local time)"""
    return f"<t:{int(datetime.timestamp())}:F>"


def discord_countdown(datetime: dt):
    """Create a discord time that shows time remaining"""
    return f"<t:{int(datetime.timestamp())}:R>"


def discord_date(datetime: dt):
    """create a discord time that displays as a date string"""
    return f"<t:{int(datetime.timestamp())}:D>"


def get_hammertime(datetime: dt):
    """Wrapper for easy use of schedule info"""
    return f"{discord_time(datetime)} ({discord_countdown(datetime)})"


def calculate_endtime(start_time: dt, duration_hours: int) -> dt:
    """Given a start time and a duration in hours calculate the finish time"""
    end_time = start_time + timedelta(hours=duration_hours)
    return end_time
