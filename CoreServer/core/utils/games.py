from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async

from core.models.game import Game
from core.models.players import Player
from core.utils.players import get_player_max_games, get_player_game_count
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
def get_upcoming_games(days=30):
    now = timezone.now()
    end = now + timedelta(days=days)
    queryset = Game.objects.filter(datetime__gte=now)
    queryset = queryset.exclude(status__in=['Cancelled', 'Draft'])
    queryset = queryset.filter(datetime__lte=end)
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_upcoming_games_for_player(player_id, waitlisted=False):
    """ Get all of the upcoming games """
    now = timezone.now()
    players = Player.objects.filter(discord_id=player_id)
    players = players.filter(standby=waitlisted)

    queryset = Game.objects.filter(players__in=players)
    queryset = queryset.filter(datetime__gte=now)
    queryset = queryset.order_by('datetime')
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_upcoming_games_for_dm(dm_id):
    now = timezone.now()
    queryset = Game.objects.filter(datetime__gte=now)
    # Ignore games still in draft or cancelled
    queryset = queryset.exclude(status='Draft').exclude(status='Cancelled')
    queryset = queryset.filter(dm__discord_id=dm_id)
    queryset = queryset.order_by('datetime')
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_outstanding_games(priority=False):
    """ Retrieve all game objects that are ready for release """
    now = timezone.now()

    # only interested in games in the future
    queryset = Game.objects.filter(datetime__gte=now)
    queryset = queryset.exclude(status__in=['Cancelled', 'Draft'])
    if priority:
        queryset = queryset.filter(datetime_release__lte=now)
    else:
        queryset = queryset.filter(datetime_open_release__lte=now)
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_current_games(priority=False):
    """ Get all games currently accepting signups """
    now = timezone.now()
    queryset = Game.objects.filter(datetime__gte=now)
    if priority:
        queryset = queryset.filter(status='Priority')
    else:
        queryset = queryset.filter(status='Released')
    # force evaluation before leaving this sync context
    return list(queryset.order_by('datetime'))

@sync_to_async
def set_game_announced(game, priority_release=False):
    """ Set this game object's status to reflect the fact it's now been published """
    if game.status == 'Priority' or not priority_release:
        game.status = 'Released'
    elif game.status == 'Pending':
        game.status = 'Priority'
    game.save()
    return game

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

    if players.filter(discord_id=user.id):
        return False, 'You are already in this game'
    if waitlist.filter(discord_id=user.id):
        return False, f"You\'re already in the waitlist for this game in position: {waitlist.get(discord_id=user.id).waitlist}"

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
    if game.status in ['Cancelled', 'Draft', 'Pending']:
        return True
    return False
