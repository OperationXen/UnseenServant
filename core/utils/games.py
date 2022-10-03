from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import sync_to_async

from core.models.game import Game
from core.models.players import Player
from discordbot.logs import logger as log
from core.utils.players import get_player_max_games, get_player_game_count
from core.utils.players import get_current_user_bans, get_user_rank
from core.utils.players import get_last_waitlist_position


@sync_to_async
def get_dm(game):
    """Get an object representing the games DM"""
    if game.dm:
        return game.dm
    return None


@sync_to_async
def get_player_list(game):
    """get a list of players subscribed to a game"""
    return list(game.players.filter(standby=False))


@sync_to_async
def get_wait_list(game):
    """fetch all waitlisted players, arranged in order of position"""
    return list(game.players.filter(standby=True).order_by("waitlist"))


@sync_to_async
def get_upcoming_games(days=30, released=False):
    now = timezone.now()
    end = now + timedelta(days=days)
    queryset = Game.objects.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.filter(datetime__lte=end)
    if released:
        released_filter = Q(datetime_release__lte=now) | Q(datetime_open_release__lte=now)
        queryset = queryset.filter(released_filter)
    queryset = queryset.order_by("datetime")
    # force evaluation before leaving this sync context
    return list(queryset)


@sync_to_async
def get_upcoming_games_for_player(player_id, waitlisted=False):
    """Get all of the upcoming games"""
    now = timezone.now()
    players = Player.objects.filter(discord_id=player_id)
    players = players.filter(standby=waitlisted)

    queryset = Game.objects.filter(players__in=players)
    queryset = queryset.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.order_by("datetime")
    # force evaluation before leaving this sync context
    return list(queryset)

@sync_to_async
def get_upcoming_games_for_dm(dm_id):
    now = timezone.now()
    queryset = Game.objects.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.filter(dm__discord_id=dm_id)
    queryset = queryset.order_by("datetime")
    # force evaluation before leaving this sync context
    return list(queryset)


@sync_to_async
def get_outstanding_games(priority=False):
    """Retrieve all game objects that are ready for release"""
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
    queryset = queryset.order_by("datetime")
    # force evaluation before leaving this sync context
    return list(queryset)


def _get_game_by_id(game_id):
    """Syncronous context worker to get game and forcibly evaluate it"""
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
def db_add_player_to_game(game, user):
    """Add a new player to an existing game"""
    try:
        players = game.players.filter(standby=False)
        waitlist = game.players.filter(standby=True)

        # If you're the DM, already playing or waitlisted you can't join
        if user.id == game.dm.discord_id:
            return False
        if players.filter(discord_id=user.id).first():
            return False
        if waitlist.filter(discord_id=user.id).first():
            return False

        # If user is banned or doesn't have enough signup credits
        if get_current_user_bans(user):
            return False
        if not get_user_rank(user) or get_player_game_count(user) >= get_player_max_games(user):
            return False

        # Add player to game, either on waitlist or party
        if players.count() >= game.max_players:
            waitlist_position = get_last_waitlist_position(game) + 1
            Player.objects.create(game=game, discord_id=user.id, discord_name=user.name, standby=True, waitlist=waitlist_position)
            return "waitlist"
        else:
            Player.objects.create(game=game, discord_id=user.id, discord_name=user.name, standby=False)
            return "party"
    except Exception as e:
        log.debug(f"Exception occured adding {user.name} to {game.name}")
        return False


@sync_to_async
def db_remove_player_from_game(game, user):
    """Remove an existing player from a game"""
    queryset = game.players.filter(standby=False)
    player = queryset.filter(discord_id=user.id).first()
    if player:
        player.delete()
        return True
    return False

@sync_to_async
def db_remove_discord_user_from_game(game, user):
    """ Remove a player from a game by their discord ID """
    player = game.players.filter(discord_id=user.id).first()
    removed_from_party = not player.waitlist
    if player:
        player.delete()
        return removed_from_party
    return None


@sync_to_async
def check_game_expired(game):
    """See if a game object has reached expiry"""
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
    """Check if the passed game is currently a patreon exclusive"""
    now = timezone.now()
    if game.datetime_release and game.datetime_release < now:
        if not game.datetime_open_release or game.datetime_open_release > now:
            return True
    return False
