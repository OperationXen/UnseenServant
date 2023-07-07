from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import sync_to_async

from discord import User as DiscordUser

from core.models import Game, Player, CustomUser
from discord_bot.logs import logger as log
from core.utils.players import get_player_max_games, get_player_game_count
from core.utils.players import get_user_highest_rank
from core.utils.players import get_last_waitlist_position
from core.utils.user import get_user_by_discord_id
from core.utils.sanctions import get_current_user_bans


def _refetch_game_data(game: Game) -> Game:
    """Refresh the game object from the database"""
    game.refresh_from_db()
    return game


@sync_to_async
def refetch_game_data(game: Game) -> Game:
    """Refresh the game object from the database"""
    return _refetch_game_data(game)


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


def _get_dm(game: Game):
    """Get the specified games DM (syncronous)"""
    try:
        if game.dm:
            return game.dm
    except Exception as e:
        pass  # Silence
    return None


@sync_to_async
def get_dm(game):
    """Async wrapper function to get the specified games' DM"""
    return _get_dm(game)


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
def get_upcoming_games_for_player(discord_id: str, waitlisted=False):
    """Get all of the upcoming games"""
    now = timezone.now()
    players = Player.objects.filter(discord_id=discord_id)
    players = players.filter(standby=waitlisted)

    queryset = Game.objects.filter(players__in=players)
    queryset = queryset.filter(ready=True).filter(datetime__gte=now)
    queryset = queryset.order_by("datetime")
    # force evaluation before leaving this sync context
    return list(queryset)


@sync_to_async
def get_upcoming_games_for_dm(dm_id: str):
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
def db_force_add_player_to_game(game: Game, user: CustomUser):
    """Force a player into a specified game, ignoring all conditions"""
    discord_id = str(user.id)
    try:
        player = game.players.get(discord_id=discord_id)
        player.standby = False
        player.save()
    except Player.DoesNotExist:
        player = Player.objects.create(game=game, discord_id=discord_id, discord_name=user.name, standby=False)
    return player


def sanity_check_new_game_player(game: Game, discord_id: str) -> bool:
    """perform a go / no go check for adding a given player to a game (by discord ID)"""
    # If use is DM, already playing or waitlisted they can't join
    if discord_id == game.dm.discord_id:
        return False
    if game.players.filter(discord_id=discord_id).first():
        return False

    # If user is banned they can't join
    if get_current_user_bans(discord_id):
        return False
    return True


def check_user_available_credit(discord_id: str) -> int:
    """Check a logged in users' available credit"""
    user = get_user_by_discord_id(discord_id)
    if not user:
        return False
    if not get_user_highest_rank(user.roles):
        return False
    return get_player_game_count(discord_id) < get_player_max_games(user)


def check_discord_user_available_credit(user: DiscordUser) -> int:
    """Check a discord user (not logged in to API) for available credit"""
    if not get_user_highest_rank(user.roles):
        return False
    discord_id = str(user.id)
    pending_games = get_player_game_count(discord_id)
    max_games = get_player_max_games(user)
    return pending_games < max_games


def handle_game_player_add(game: Game, discord_id: str, discord_name: str) -> Player | None:
    """Handle the process of verifying and adding a player to a game"""
    try:
        if not sanity_check_new_game_player(game, discord_id):
            return None

        # Add player to game, either on waitlist or party
        current_players = game.players.filter(standby=False).count()
        if current_players >= game.max_players:
            waitlist_position = get_last_waitlist_position(game) + 1
            player = Player.objects.create(
                game=game, discord_id=discord_id, discord_name=discord_name, standby=True, waitlist=waitlist_position
            )
        else:
            player = Player.objects.create(game=game, discord_id=discord_id, discord_name=discord_name, standby=False)
        return player
    except Exception as e:
        log.debug(f"Exception occured adding {discord_name} to {game.name}")
        return None


@sync_to_async
def db_add_player_to_game(game: Game, user: DiscordUser):
    """Add a new player to an existing game"""
    discord_id = str(user.id)
    credit_available = check_discord_user_available_credit(user)
    if not credit_available:
        log.debug(f"{user.name} attempted to sign up for {game.name}, but has insufficient credit")
        return False
    player = handle_game_player_add(game, discord_id, user.name)
    return player


@sync_to_async
def db_remove_discord_user_from_game(game: Game, discord_id: str):
    """Remove a player from a game by their discord ID"""
    player = game.players.filter(discord_id=discord_id).first()
    if player:
        removed_from_party = not player.waitlist
        player.delete()
        return removed_from_party
    return None


@sync_to_async
def check_game_expired(game: Game) -> bool:
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
