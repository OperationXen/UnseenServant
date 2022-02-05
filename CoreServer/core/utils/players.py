from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import sync_to_async

from discordbot.utils.messaging import send_dm
from discordbot.utils.time import discord_countdown
from core.models.game import Game
from core.models.players import Player, Ban, Rank, Strike

def get_current_user_bans(user):
    """ Check a given discord user is in good standing - Needs to be syncronous """
    now = timezone.now()
    not_expired = Q(datetime_end__gte=now) | Q(datetime_end=None)

    queryset = Ban.objects.filter(discord_id=user.id).filter(datetime_start__lte=now)
    queryset = queryset.filter(not_expired)
    return queryset.order_by('datetime_end')

def get_all_current_bans():
    """ Retrieve all currently outstanding bans """
    now = timezone.now()
    not_expired = Q(datetime_end__gte=now) | Q(datetime_end=None)

    queryset = Ban.objects.filter(datetime_start__lte=now)
    queryset = queryset.filter(not_expired)
    return queryset.order_by('datetime_end')

def add_new_ban(user, variant, reason, admin, ban_length):
    """ Add a new ban """
    now = timezone.now()
    if ban_length == -1 or variant == 'PM':
        variant = 'PM'
        end = None
    else:
        end = now + timedelta(days=ban_length)
    # Remove player from games on hard ban
    if variant == 'HD' or variant == 'PM':
        queryset = Player.objects.filter(discord_id = user.id).filter(game__datetime__gte=now)
        queryset.delete()

    Ban.objects.create(discord_id=user.id, discord_name=f"{user.name}#{user.discriminator}", 
                    issuer_id=admin.id, issuer_name=f"{admin.name}#{admin.discriminator}",
                    reason=reason, variant=variant, datetime_end=end)

@sync_to_async
def get_outstanding_bans(user = None):
    if user:
        bans = get_current_user_bans(user)
    else:
        bans = get_all_current_bans()
    # force queryset evaluation before returning to async
    return list(bans)

@sync_to_async
def issue_player_ban(user, variant, reason, admin, ban_length):
    """ Ban a player from using the signup bot """
    add_new_ban(user, variant, reason, admin, ban_length)

def get_player_game_count(discord_user):
    """ get the total number of games a player is in """
    now = timezone.now() 
    queryset = Player.objects.filter(discord_id = discord_user.id)
    queryset = queryset.filter(game__datetime__gte=now)
    return queryset.count()

def get_user_rank(discord_user):
    """ go through user roles and identify their best rank """
    roles = [role.name.lower() for role in discord_user.roles]
    ranks = Rank.objects.all().order_by('-priority')
    for rank in ranks:
        if rank.name.lower() in roles:
            return rank
    return None

def get_waitlist_position(discord_user):
    """ get the waitlist position for a given discord user """
    player = Player.objects.filter(discord_id = discord_user.id)

def get_player_max_games(discord_user):
    """ get the total number of games a user can sign up for """
    rank = get_user_rank(discord_user)
    if rank:
        return rank.max_games
    return 0

def get_player_available_games(discord_user):
    """ Get the games available for a given user """
    now = timezone.now()
    max_games = get_player_max_games(discord_user)
    queryset = Player.objects.filter(discord_id=discord_user.id)
    queryset = queryset.filter(game__datetime__gte=now)
    pending_games = queryset.count()
    return max_games - pending_games

@sync_to_async
def get_player_signups_remaining(user):
    """ Get the total number of signups the user has availble to them """
    return get_player_available_games(user)

@sync_to_async
def get_player_credit_text(user):
    """ Get a text string explaining to the user how many game credits they have """
    credits = get_player_available_games(user)
    if credits:
        return f"You have [{credits}] game credits available"
    else:
        return 'You have no remaining game credits'
    
def promote_from_waitlist(game):
    """ Identify the next player in line to join the specified game """
    player = Player.objects.filter(game=game).filter(standby=True).order_by('waitlist').first()
    if player:
        player.standby = False
        player.save()
        send_dm(player.id, f"You have been promoted from the waitlist for {game.name} in {discord_countdown(game.datetime)}!")

def process_player_removal(player):
    """ remove a player from a game and promote from waitlist """
    game = player.game
    player.delete()
    promote_from_waitlist(game)

def get_waitlist_rank(player):
    """ get the rank of the player in the waitlist """
    queryset = Player.objects.filter(game = player.game).filter(standby=True)
    waitlist = list(queryset.order_by('waitlist'))
    return waitlist.index(player) + 1

def get_last_waitlist_position(game):
    """ get the position at the end of the waitlist """
    queryset = Player.objects.filter(game=game).filter(standby=True)
    last_player = queryset.order_by('waitlist').last()
    if last_player:
        return last_player.waitlist
    return 0
