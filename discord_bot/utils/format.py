import urllib.parse

from config.settings import SERVER_URI


def create_google_calendar_link(game):
    """build a google calendar link for an event"""
    link = f"https://www.google.com/calendar/render?"
    params = {}
    params["action"] = "TEMPLATE"
    params["text"] = game.name
    params["details"] = f"Triden%20games%20DMed%20by%20{game.dm.name}"
    params["location"] = f"Triden Games"
    params["dates"] = f"{game.datetime.strftime('%Y%m%dT%H%M')}Z/{game.datetime.strftime('%Y%m%dT%H%M')}Z"
    params["sf"] = "true"

    return link + urllib.parse.urlencode(params)


def generate_calendar_message(game):
    """Create a series of links to automatically add game to various calendars"""
    message = f"Click to add event for {game.name} to [Google Calendar](<{create_google_calendar_link(game)}>)"
    # message = message + f" / [Apple Calendar](<https://www.apple.com>)"
    # message = message + f" / [Outlook Calendar](<https://www.live.com>)"
    return message


def documentation_url():
    """Generate a link to the documentation"""
    return "https://tinyurl.com/TridenBotGuide"


def admin_panel_url():
    """Generate a link to the admin panel"""
    try:
        return f"https://{SERVER_URI}/admin"
    except IndexError:
        return f""
