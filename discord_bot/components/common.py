from discord import Member as DiscordMember
from core.models import Game

from discord_bot.utils.channel import async_remove_discord_member_from_game_channel
from discord_bot.utils.players import async_do_waitlist_updates
from discord_bot.utils.games import async_remove_discord_member_from_game
from discord_bot.utils.messaging import async_send_dm
from core.utils.channels import async_get_game_channel_for_game
from core.utils.players import async_get_player_credit_text
from core.utils.games import async_player_dropout_permitted

from discord_bot.logs import logger as log


async def handle_player_dropout_event(game: Game, discord_member: DiscordMember) -> bool:
    """handle a player clicking the dropout button"""
    try:
        if await async_player_dropout_permitted(game):
            removed = await async_remove_discord_member_from_game(discord_member, game)
            await async_do_waitlist_updates(game)
            if removed:
                log.info(f"[>] User {discord_member.name} dropped from {game.name}")
                games_remaining_text = await async_get_player_credit_text(discord_member)
                await async_send_dm(discord_member, f"Removed you from {game.name} `({games_remaining_text})`")

                game_channel = await async_get_game_channel_for_game(game)
                if game_channel:
                    await async_remove_discord_member_from_game_channel(discord_member, game_channel)
            else:
                log.debug(f"[!] Unable to remove {discord_member.name} from {game.name}")
            return removed
        else:
            log.info(f"[>] {discord_member.name} not permitted to drop from {game.name}")
            await async_do_waitlist_updates(game)
            await async_send_dm(discord_member, f"You cannot drop from {game.name} as it in the past")
            return False
    except Exception as e:
        log.error(f"[!] Exception occured handling dropout event: {e}")
