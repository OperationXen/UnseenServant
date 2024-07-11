from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Q, QuerySet
from asgiref.sync import sync_to_async

from discord import User as DiscordUser

from core.models import Game, Player, CustomUser
from discord_bot.logs import logger as log
from core.utils.players import get_player_max_games, get_player_game_count
from core.utils.players import get_user_highest_rank
from core.utils.user import get_user_available_credit
from core.utils.sanctions import get_current_user_bans


# ########################################################################## #
def refetch_game_data(game: Game) -> Game:
    """Refresh the game object from the database"""
    game_name = game.name
    try:
        game.refresh_from_db()
        return game
    except:
        log.debug(f"Exception occured refetching {game_name} from DB")
        return None


@sync_to_async
def async_refetch_game_data(game: Game) -> Game:
    """Refresh the game object from the database"""
    return refetch_game_data(game)


# ########################################################################## #
def calc_game_tier(game: Game) -> int | None:
    """Calculates a game's tier"""
    if game.level_min >= 17:
        return 4
    if game.level_min >= 11:
        return 3
    if game.level_min >= 5:
        return 2
    if game.level_min:
        return 1
    return None


# ########################################################################## #
def get_dm(game: Game):
    """Get the specified games DM (syncronous)"""
    try:
        if game.dm:
            return game.dm
    except Exception as e:
        pass  # Silence
    return None


@sync_to_async
def async_get_dm(game):
    """Async wrapper function to get the specified games' DM"""
    return get_dm(game)


# ########################################################################## #
def get_player_list(game: Game) -> QuerySet:
    """Get a list of players for a specified game"""
    queryset = game.players.filter(standby=False)
    return queryset


@sync_to_async
def async_get_player_list(game) -> list[Player]:
    """get a list of players subscribed to a game"""
    queryset = get_player_list(game)
    return list(queryset)


# ########################################################################## #
def get_wait_list(game: Game) -> QuerySet:
    """Get the waitlist for the specified game"""
    queryset = game.players.filter(standby=True).order_by("waitlist")
    return queryset


@sync_to_async
def async_get_wait_list(game: Game) -> list[Player]:
    """async wrapper to fetch all waitlisted players, arranged in order of position"""
    queryset = get_wait_list(game)
    return list(queryset)


# ########################################################################## #
def get_historic_games(days: int = 30, start_date: datetime | None = None) -> QuerySet:
    """Get games which have been played over the last X days"""
    if start_date:
        start = start_date
        end = start + timedelta(days=days)
    else:
        now = timezone.now()
        start = now - timedelta(days=days)
        end = now
    queryset = Game.objects.filter(datetime__gte=start).filter(datetime__lte=end)
    queryset = queryset.order_by("datetime")
    return queryset


@sync_to_async
def async_get_historic_games(days: int = 30) -> list[Game]:
    """async wrapper to get historic game information"""
    queryset = get_historic_games(days=days)
    # force evaluation before leaving this sync context
    return list(queryset)


# ########################################################################## #
def get_upcoming_games(days: int = 30, released: bool = False) -> QuerySet:
    """get upcoming games"""
    now = timezone.now()
    end = now + timedelta(days=days)
    queryset = Game.objects.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.filter(datetime__lte=end)
    if released:
        released_filter = Q(datetime_release__lte=now) | Q(datetime_open_release__lte=now)
        queryset = queryset.filter(released_filter)
    queryset = queryset.order_by("datetime")
    return queryset


@sync_to_async
def async_get_upcoming_games(days: int = 30, released: bool = False) -> list[Game]:
    """asyncronous wrapper to get upcoming games"""
    queryset = get_upcoming_games(days, released)
    # force evaluation before leaving this sync context
    return list(queryset)


# ########################################################################## #
def get_upcoming_games_for_discord_id(discord_id: str, waitlisted: bool = False) -> QuerySet:
    """Get all of the upcoming games for a specified discord ID"""
    now = timezone.now()
    players = Player.objects.filter(discord_id=discord_id)
    players = players.filter(standby=waitlisted)

    queryset = Game.objects.filter(players__in=players)
    queryset = queryset.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.order_by("datetime")
    return queryset


@sync_to_async
def async_get_upcoming_games_for_discord_id(discord_id: str, waitlisted=False) -> list[Game]:
    """Async wrapper to get games for discord ID"""
    queryset = get_upcoming_games_for_discord_id(discord_id, waitlisted)
    # force evaluation before leaving this sync context
    return list(queryset)


# ########################################################################## #
def get_upcoming_games_for_dm_discord_id(discord_id: str) -> list[Game]:
    now = timezone.now()
    queryset = Game.objects.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.filter(dm__discord_id=discord_id)
    queryset = queryset.order_by("datetime")
    return queryset


@sync_to_async
def async_get_upcoming_games_for_dm_discord_id(discord_id: str) -> list[Game]:
    """Async wrapper for find upcoming games for a DM by their discord ID"""
    queryset = get_upcoming_games_for_dm_discord_id(discord_id)
    # force evaluation before leaving this sync context
    return list(queryset)


# ########################################################################## #
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


# ########################################################################## #
def get_game_by_id(game_id):
    """Syncronous context worker to get game and forcibly evaluate it"""
    try:
        game = Game.objects.get(pk=game_id)
        # Use conditional logic to force execution of lazy query, note we also need to evaluate linked DM model
        if game and game.dm:
            return game
    except Game.DoesNotExist:
        return None


@sync_to_async
def async_get_game_by_id(game_id):
    return get_game_by_id(game_id)


def game_has_player_by_discord_id(game: Game, discord_id: str) -> bool:
    """Check to see if a specific game has a player by their discord ID"""
    existing = game.players.filter(discord_id=discord_id).first()
    if existing:
        return True
    return False


# ########################################################################## #
@sync_to_async
def async_db_force_add_player_to_game(game: Game, user: CustomUser):
    """Force a player into a specified game, ignoring all conditions"""
    discord_id = str(user.id)
    try:
        player = game.players.get(discord_id=discord_id)
        player.standby = False
        player.save()
    except Player.DoesNotExist:
        player = Player.objects.create(game=game, discord_id=discord_id, discord_name=user.name, standby=False)
    return player


def user_can_join_game(user: CustomUser, game: Game) -> bool:
    """perform a go / no go check for adding a given player to a game (by discord ID)"""
    # If use is DM, already playing or waitlisted they can't join
    if user == game.dm.user:
        return False
    if Player.objects.filter(game=game).filter(user=user).exists():
        return False
    if get_user_available_credit(user) <= 0:
        return False

    # If user is banned they can't join
    if get_current_user_bans(user.discord_id):
        return False
    return True


def check_discord_user_available_credit(user: DiscordUser) -> int:
    """Check a discord user (not logged in to API) for available credit"""
    if not get_user_highest_rank(user.roles):
        return False
    discord_id = str(user.id)
    pending_games = get_player_game_count(discord_id)
    max_games = get_player_max_games(user)
    return pending_games < max_games


# ########################################################################## #
def check_game_expired(game: Game) -> bool:
    """See if a game object has reached expiry"""
    game = get_game_by_id(game.id)
    if not game:
        return True
    expiry = timezone.now() - timedelta(days=1)
    if game.datetime < expiry:
        return True
    if not game.ready:
        return True
    return False


@sync_to_async
def async_check_game_expired(game: Game) -> bool:
    """Async wrapper for checking if a game has expired"""
    return check_game_expired(game)


# ########################################################################## #
def check_game_pending(game: Game) -> bool:
    """See if a game is in the future or not"""
    now = timezone.now()
    if game.datetime > now:
        return True
    return False


def is_patreon_exclusive(game: Game) -> bool:
    """Check if the passed game is currently a patreon exclusive"""
    now = timezone.now()
    if game.datetime_release and game.datetime_release < now:
        if not game.datetime_open_release or game.datetime_open_release > now:
            return True
    return False
