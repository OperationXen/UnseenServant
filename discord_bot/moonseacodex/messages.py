from discord_bot.utils.session_log import validate_game_log

from discord_bot.moonseacodex.session_log_parser import get_game_from_message
from discord_bot.utils.moonseacodex import async_create_msc_game
from discord_bot.components.moonseacodex.games import MSCGameJoinEmbed

from discord_bot.logs import logger as log


async def handle_game_log_posted(message):
    log.debug(f"[-] Handling game log posted to channel")
    if not validate_game_log(message):
        log.debug(f"[!] Game log validation failed")
        return False

    game = get_game_from_message(message)
    log.debug(f"[-] Game log post parsed: {game.name}")
    if game:
        log.debug(f"[-] Creating game in Moonsea Codex")
        game_uuid = await async_create_msc_game(game)
        if game_uuid:
            log.info(f"[+] Game successfully added to Moonsea Codex: {game.name} ({game_uuid})")
            embed = MSCGameJoinEmbed(game, game_uuid)
            try:
                await message.reply(embed=embed, mention_author=False)
                return True
            except Exception as e:
                log.error(f"[!] Failed to send reply to original log post: {e}")
                return False
        else:
            log.error(f"[!] Failed to create game in Moonsea Codex")
    return False
