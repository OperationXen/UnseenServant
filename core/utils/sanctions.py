from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import timedelta

from core.models.players import Strike, Ban

def get_current_user_strikes(discord_id: str):
    """ get the total number of outstanding strikes for a given user """
    now = timezone.now()
    queryset = Strike.objects.filter(discord_id=discord_id)
    queryset = queryset.filter(expires__gte=now).filter(datetime__lte=now)
    # force evaluation before leaving this syncronous context
    return queryset.order_by('expires')

def clear_user_strikes(user):
    """ Given a user, expire all of their outstanding strikes """
    now = timezone.now()
    for strike in get_current_user_strikes(str(user.id)):
        strike.expires = now
        strike.save()

def check_strike_threshold(user, admin):
    """ Checks a given user's strikes and issues bans as needed """
    now = timezone.now()
    end = now + timedelta(weeks = 12)
    outstanding = get_current_user_strikes(str(user.id))
    if len(outstanding) >= 3:
        Ban.objects.create(discord_id=str(user.id), discord_name=f"{user.name}#{user.discriminator}", 
                    issuer_id=admin.id, issuer_name=f"{admin.name}#{admin.discriminator}",
                    reason='Three strikes and you\'re out...', variant='ST', datetime_end=end)
        clear_user_strikes(user)
        return True
    return False

def add_user_strike(user, reason, admin):
    """ Create a new user strike object """
    now = timezone.now()
    end = now + timedelta(weeks = 52)
    Strike.objects.create(discord_id=str(user.id), discord_name=f"{user.name}#{user.discriminator}", 
                        issuer_id=admin.id, issuer_name=f"{admin.name}#{admin.discriminator}",
                        reason=reason, expires=end)    

@sync_to_async
def issue_player_strike(user, reason, admin):
    """ Issue a strike to the player """
    add_user_strike(user, reason, admin)
    return check_strike_threshold(user, admin)

@sync_to_async
def get_outstanding_strikes(user):
    """ Get outstanding strikes for the user """
    strikes = get_current_user_strikes(str(user.id))
    # force to list to evaluate before leaving async context
    return list(strikes)
