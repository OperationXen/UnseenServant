from datetime import datetime
from asgiref.sync import sync_to_async

from core.models.players import Player, Ban, Rank


@sync_to_async
def get_outstanding_bans():
    now = datetime.now()
    queryset = Ban.objects.filter(datetime_end__gte=now).filter(datetime_start__lte=now)
    # force evaluation before leaving this syncronous context
    return list(queryset)

@sync_to_async
def get_bans_for_user(user, all=False):
    """ Check a given discord user is in good standing """
    now = datetime.now()
    queryset= Ban.object.filter(discord_id=user.id)
    if not all:
        queryset = queryset.filter(datetime_end__gte=now)
        queryset = queryset.filter(datetime_start__lte=now)
    # force evaluation before leaving this syncronous context
    return list(queryset.order_by('datetime_end'))   

@sync_to_async
def get_player_game_count(discord_user):
    """ get the total number of games a player is in """
    now = datetime.now() 
    queryset = Player.objects.filter(discord_id = discord_user.id)
    queryset = queryset.filter(game__datetime__gte=now)
    return queryset.count()

@sync_to_async
def get_user_rank(discord_user):
    """ go through user roles and identify their best rank """
    ranks = Rank.objects.all().order_by('priority')
    for rank in ranks:
        if rank.name in discord_user.roles:
            return rank
    return None

@sync_to_async
def get_player_max_games(discord_user):
    """ get the total number of games a user can sign up for """
    rank = get_user_rank(discord_user)
    if rank:
        return rank.max_games
    return 0