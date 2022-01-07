from datetime import datetime, timedelta

def a_year_from_now():
    """ get a timestamp 1 year hence """
    now = datetime.now()
    return now + timedelta(years = 1)

def a_month_from_now():
    """ get a timestamp 1 month hence """
    now = datetime.now()
    return now + timedelta(months = 1)

def discord_time(datetime):
    """ Create a discord time (adjusts to local time) """
    return f"<t:{int(datetime.timestamp())}:F>"

def discord_countdown(datetime):
    """ Create a discord time that shows time remaining """
    return f"<t:{int(datetime.timestamp())}:R>"
