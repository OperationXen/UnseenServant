from django.utils import timezone
from asgiref.sync import sync_to_async

from discordbot.utils.messaging import send_dm
from core.utils.time import discord_countdown
from core.models.game import Game
from core.models.players import Player, Ban, Rank

@sync_to_async
def get_outstanding_bans():
    now = timezone.now()
    queryset = Ban.objects.filter(datetime_end__gte=now).filter(datetime_start__lte=now)
    # force evaluation before leaving this syncronous context
    return list(queryset)

@sync_to_async
def get_bans_for_user(user, all=False):
    """ Check a given discord user is in good standing """
    now = timezone.now()
    queryset= Ban.objects.filter(discord_id=user.id)
    if not all:
        queryset = queryset.filter(datetime_end__gte=now)
        queryset = queryset.filter(datetime_start__lte=now)
    # force evaluation before leaving this syncronous context
    return list(queryset.order_by('datetime_end'))   

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
