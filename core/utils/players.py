from datetime import timedelta

from asgiref.sync import sync_to_async
from django.db.models import Q, Sum
from django.utils import timezone

from core.models.players import Ban, BonusCredit, Player, Rank
from discordbot.logs import logger as log


def get_current_user_bans(user):
    """Check a given discord user is in good standing - Needs to be syncronous"""
    now = timezone.now()
    not_expired = Q(datetime_end__gte=now) | Q(datetime_end=None)

    queryset = Ban.objects.filter(discord_id=user.id).filter(datetime_start__lte=now)
    queryset = queryset.filter(not_expired)
    return queryset.order_by("datetime_end")


def get_all_current_bans():
    """Retrieve all currently outstanding bans"""
    now = timezone.now()
    not_expired = Q(datetime_end__gte=now) | Q(datetime_end=None)

    queryset = Ban.objects.filter(datetime_start__lte=now)
    queryset = queryset.filter(not_expired)
    return queryset.order_by("datetime_end")


def add_new_ban(user, variant, reason, admin, ban_length):
    """Add a new ban"""
    now = timezone.now()
    if ban_length == -1 or variant == "PM":
        variant = "PM"
        end = None
    else:
        end = now + timedelta(days=ban_length)
    # Remove player from games on hard ban
    if variant == "HD" or variant == "PM":
        queryset = Player.objects.filter(discord_id=user.id).filter(game__datetime__gte=now)
        queryset.delete()

    Ban.objects.create(
        discord_id=user.id,
        discord_name=f"{user.name}#{user.discriminator}",
        issuer_id=admin.id,
        issuer_name=f"{admin.name}#{admin.discriminator}",
        reason=reason,
        variant=variant,
        datetime_end=end,
    )


@sync_to_async
def get_outstanding_bans(user=None):
    if user:
        bans = get_current_user_bans(user)
    else:
        bans = get_all_current_bans()
    # force queryset evaluation before returning to async
    return list(bans)


@sync_to_async
def issue_player_ban(user, variant, reason, admin, ban_length):
    """Ban a player from using the signup bot"""
    add_new_ban(user, variant, reason, admin, ban_length)


@sync_to_async
def issue_player_bonus_credit(user, number, issuer, reason="Not supplied", valid_for=None):
    """Give a player some bonus credits"""
    if valid_for:
        now = timezone.now()
        end_date = now + timedelta(days=valid_for)
    else:
        end_date = None
    obj = BonusCredit.objects.create(
        discord_id=user.id,
        discord_name=f"{user.name}#{user.discriminator}",
        issuer_id=issuer.id,
        issuer_name=f"{issuer.name}#{issuer.discriminator}",
        credits=number,
        reason=reason,
        expires=end_date,
    )
    return obj


def get_player_game_count(discord_user):
    """get the total number of games a player is in"""
    now = timezone.now()
    queryset = Player.objects.filter(discord_id=discord_user.id)
    queryset = queryset.filter(game__datetime__gte=now)
    return queryset.count()


def get_user_highest_rank(discord_user_roles: list) -> Rank | None:
    """go through user roles and identify their best rank"""
    roles = [role.name.lower() for role in discord_user_roles]
    ranks = Rank.objects.all().order_by("-priority")
    for rank in ranks:
        if rank.name.lower() in roles:
            return rank
    return None

def get_bonus_credits(discord_id: str) -> int:
    """Get the total number of bonus games awarded to the user and currently valid"""
    now = timezone.now()
    queryset = BonusCredit.objects.filter(discord_id=discord_id)
    not_expired = Q(expires__gte=now) | Q(expires=None)
    queryset = queryset.filter(not_expired)
    total = queryset.aggregate(Sum("credits"))
    return total["credits__sum"] or 0

def get_player_max_games(discord_user) -> int:
    """get the total number of games a user can sign up for"""
    max_games = 0
    rank = get_user_highest_rank(discord_user.roles)
    if rank:
        max_games = max_games + rank.max_games
    bonuses = get_bonus_credits(str(discord_user.id))
    return max_games + bonuses

def get_user_pending_games_count(discord_id: str) -> int:
    now = timezone.now()

    queryset = Player.objects.filter(discord_id=discord_id)
    queryset = queryset.filter(game__datetime__gte=now)
    pending_games = queryset.count()
    return pending_games

def get_user_signups_remaining(user):
    """Get the total number of signups the user has availble to them"""
    max_games = get_player_max_games(user)
    game_count = get_user_pending_games_count(str(user.id))
    
    log.info(f"{user} is signed up for {game_count}")
    return max_games - game_count

@sync_to_async
def get_player_credit_text(user):
    """Get a text string explaining to the user how many game credits they have"""
    credits = get_user_signups_remaining(user)
    max_games = get_player_max_games(user)
    if credits:
        return f"{credits} / {max_games} game credits available"
    else:
        return f"You have no game credits available from your [{max_games}] total"

@sync_to_async
def populate_game_from_waitlist(game):
    """fill a game up using the waitlist, return a list of the promoted players"""
    promoted = []
    players = Player.objects.filter(game=game).filter(standby=False)

    while len(players) < game.max_players:
        next = Player.objects.filter(game=game).filter(standby=True).order_by("waitlist").first()
        if next:
            next.standby = False
            next.save()
            promoted.append(next)
            players = Player.objects.filter(game=game).filter(standby=False)
        else:
            log.info("Not enough waitlisted players to fill game")
            break
    return promoted


def get_waitlist_rank(player):
    """get the rank of the player in the waitlist"""
    queryset = Player.objects.filter(game=player.game).filter(standby=True)
    waitlist = list(queryset.order_by("waitlist"))
    return waitlist.index(player) + 1


def get_last_waitlist_position(game):
    """get the position at the end of the waitlist"""
    queryset = Player.objects.filter(game=game).filter(standby=True)
    last_player = queryset.order_by("waitlist").last()
    if last_player:
        return last_player.waitlist
    return 0
