import urllib.parse

def create_google_calendar_link(game):
    """ build a google calendar link for an event """
    link = f"https://www.google.com/calendar/render?"
    params = {}
    params['action'] = 'TEMPLATE'
    params['text'] = game.name
    params['details'] = f"Triden%20games%20DMed%20by%20{game.dm.name}"
    params['location'] = f"Discord channel: {game.channel}"
    params['dates'] = f"{game.datetime.strftime('%Y%m%dT%H%M')}Z/{game.datetime.strftime('%Y%m%dT%H%M')}Z"
    params['sf'] = 'true'

    return link + urllib.parse.urlencode(params)

def generate_calendar_message(game):
    message = f"Click to add to [Google Calendar]({create_google_calendar_link(game)})"
    return message
