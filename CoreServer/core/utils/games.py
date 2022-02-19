from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import sync_to_async

from core.models.game import Game
from core.models.players import Player
from core.utils.players import get_player_max_games, get_player_game_count, get_player_available_games
from core.utils.players import get_current_user_bans, get_user_rank, process_player_removal
from core.utils.players import get_waitlist_rank, get_last_waitlist_position


@sync_to_async
def get_dm(game):
    """ Get an object representing the games DM """
    if game.dm:
        return game.dm
    return None

@sync_to_async
def get_player_list(game):
    """ get a list of players subscribed to a game """
    return list(game.players.filter(standby=False))

@sync_to_async
def get_wait_list(game):
    """ fetch all waitlisted players, arranged in order of position """
    return list(game.players.filter(standby=True).order_by('waitlist'))

@sync_to_async
def get_upcoming_games(days=30, released=False):
    now = timezone.now()
    end = now + timedelta(days=days)
    queryset = Game.objects.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.filter(datetime__lte=end)
    if released:
        released_filter = Q(datetime_release__lte=now) | Q(datetime_open_release__lte=now)
        queryset = queryset.filter(released_filter)
    queryset = queryset.order_by('datetime')
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_upcoming_games_for_player(player_id, waitlisted=False):
    """ Get all of the upcoming games """
    now = timezone.now()
    players = Player.objects.filter(discord_id=player_id)
    players = players.filter(standby=waitlisted)

    queryset = Game.objects.filter(players__in=players)
    queryset = queryset.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.order_by('datetime')
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_upcoming_games_for_dm(dm_id):
    now = timezone.now()
    queryset = Game.objects.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.filter(dm__discord_id=dm_id)
    queryset = queryset.order_by('datetime')
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_outstanding_games(priority=False):
    """ Retrieve all game objects that are ready for release """
    now = timezone.now()

    # only interested in games in the future
    queryset = Game.objects.filter(ready=True)
    queryset = queryset.filter(datetime__gte=now)
    if priority:
        # include anything ready for priority release, but not yet ready to go to general
        queryset = queryset.filter(datetime_release__lte=now)
        queryset = queryset.exclude(datetime_open_release__lte=now)
    else:
        queryset = queryset.filter(datetime_open_release__lte=now)
    queryset = queryset.order_by('datetime')
    # force evaluation before leaving this sync context
    return list(queryset)

def _get_game_by_id(game_id):
    """ Syncronous context worker to get game and forcibly evaluate it"""
    try:
        game = Game.objects.get(pk=game_id)
        # Use conditional logic to force execution of lazy query, note we also need to evaluate linked DM model
        if game and game.dm:
            return game
    except Game.DoesNotExist:
        return None

@sync_to_async
def get_game_by_id(game_id):
    return _get_game_by_id(game_id)

@sync_to_async
def add_player_to_game(game, user):
    """ Add a new player to an existing game """
    max_players = (game.max_players)
    players = game.players.filter(standby=False)
    waitlist = game.players.filter(standby=True)

    if user.id == game.dm.discord_id:
        return True, 'You are DMing this game and therefore cannot play in it. Sorry.'
    if players.filter(discord_id=user.id):
        return False, 'You are already in this game'
    waitlisted = waitlist.filter(discord_id=user.id).first()
    if waitlisted:
        return False, f"You\'re already in the waitlist for this game in position: {get_waitlist_rank(waitlisted)}"

    outstanding_bans = get_current_user_bans(user)
    if outstanding_bans:
        message = "Sorry, you are currently banned from using this bot to register for games."
        if outstanding_bans[0].variant != 'PM':
            message = message + f"\nYour ban expires {outstanding_bans[0].datetime_end.strftime('%Y-%m-%d %H:%M')}"
        return False, message

    max_games = get_player_max_games(user)
    player_games = get_player_game_count(user)
    player_rank = get_user_rank(user)
    if not player_rank:
        return False, 'You cannot sign up to any games as you do not have a rank'
    if player_games >= max_games:
        return False, f"You are already signed up for {player_games} games, the most your rank of {player_rank.name} permits"

    name = f"{user.name}:{user.discriminator}"
    if players.count() >= max_players:
        player = Player.objects.create(game=game, discord_id = user.id, discord_name = name, character = None, standby=True, waitlist=get_last_waitlist_position(game)+1)
        return True, f"Added you to the waitlist for {game.name}, you are in position: {get_waitlist_rank(player)}"
    else:
        player = Player.objects.create(game=game, discord_id = user.id, discord_name = name, character = None, standby=False)
        return True, f"Added you to {game.name}, enjoy!"

@sync_to_async
def drop_from_game(game, user):
    """ Remove an existing player from a game """
    players = game.players.filter(standby=False)
    waitlist = game.players.filter(standby=True)

    player = waitlist.filter(discord_id=user.id).first()
    if player:
        player.delete()
        return True, f"You have been removed from the waitlist for {game.name}"    

    player = players.filter(discord_id=user.id).first()
    if player:
        process_player_removal(player)
        return True, f"You have dropped out of {game.name}"
    return False, f"You aren't queued for this game..."

@sync_to_async
def check_game_expired(game):
    """ See if a game object has reached expiry """
    game = _get_game_by_id(game.id)
    if not game:
        return True
    expiry = timezone.now() - timedelta(days=1)
    if game.datetime < expiry:
        return True
    if not game.ready:
        return True
    return False

def is_patreon_exclusive(game):
    """ Check if the passed game is currently a patreon exclusive """
    now = timezone.now()
    if game.datetime_release and game.datetime_release < now:
        if not game.datetime_open_release or game.datetime_open_release > now:
            return True
    return False
