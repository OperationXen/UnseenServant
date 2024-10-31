from asyncio import gather, create_task

from discord import Member as DiscordMember
from core.models import Game
from core.errors import ChannelError

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
    pending = []
    retval = None
    try:
        if await async_player_dropout_permitted(game):
            removed = await async_remove_discord_member_from_game(discord_member, game)
            pending.append(create_task(async_do_waitlist_updates(game)))
            if removed:
                log.info(f"[>] User {discord_member.name} dropped from {game.name}")
                games_remaining_text = await async_get_player_credit_text(discord_member)
                pending.append(
                    create_task(
                        async_send_dm(discord_member, f"Removed you from {game.name} `({games_remaining_text})`")
                    )
                )
                try:
                    game_channel = await async_get_game_channel_for_game(game)
                    pending.append(
                        create_task(async_remove_discord_member_from_game_channel(discord_member, game_channel))
                    )
                except ChannelError:
                    pass  # no game channel exists, this is fine.
            else:
                log.debug(f"[!] Unable to remove {discord_member.name} from {game.name}")
            retval = removed
        else:
            log.info(f"[>] {discord_member.name} not permitted to drop from {game.name}")
            pending.append(create_task(async_do_waitlist_updates(game)))
            pending.append(
                create_task(async_send_dm(discord_member, f"You cannot drop from {game.name} as it in the past"))
            )
            retval = False

        await gather(*pending)
        return retval
    except Exception as e:
        log.error(f"[!] Exception occured handling dropout event: {e}")
