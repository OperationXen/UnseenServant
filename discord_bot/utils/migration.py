from asgiref.sync import sync_to_async
from django.utils import timezone

from core.models import Player, CustomUser

from config.settings import DISCORD_GUILDS
from discord_bot.bot import bot
from discord_bot.logs import logger as log
from discord_bot.utils.auth import create_user_from_discord_member


async def get_discord_member_by_id(player_id):
    log.debug(f"[.] Fetching discord details for {player_id}")
    guild_id = int(DISCORD_GUILDS[0])
    guild = bot.get_guild(guild_id)
    member = await guild.fetch_member(player_id)
    return member


@sync_to_async
def get_players_to_update():
    now = timezone.now()
    queryset = Player.objects.filter(game__datetime__gte=now).distinct()
    queryset = Player.objects.filter(user=None)
    return list(queryset)


@sync_to_async
def update_player_objects(discord_user):
    log.debug(f"[.] Updating player objects for {discord_user.name}")
    try:
        user = CustomUser.objects.get(discord_id=discord_user.id)
        log.debug(f"[..] Existing user found, using this")
    except CustomUser.DoesNotExist:
        user = create_user_from_discord_member(discord_user)
        if user:
            log.debug(f"[..] Created new user")
        else:
            log.debug(f"[.!] Skipping due to user creation failure")
            return
    references = Player.objects.filter(discord_id=user.discord_id)
    references.update(user=user)
    log.debug(f"[-] Update complete!")


async def create_missing_users():
    to_process = await get_players_to_update()
    for player in to_process:
        try:
            discord_member = await get_discord_member_by_id(player.discord_id)
            await update_player_objects(discord_member)
        except Exception as e:
            log.error(f"[!] Exception occured during update process: {str(e)}")
