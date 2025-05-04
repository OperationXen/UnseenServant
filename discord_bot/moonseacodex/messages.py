from discord_bot.utils.session_log import validate_game_log

from discord_bot.moonseacodex.session_log_parser import get_game_from_message
from discord_bot.utils.moonseacodex import async_create_msc_game


async def handle_game_log_posted(message):
    if not validate_game_log(message):
        return False

    game = get_game_from_message(message)
    if game:
        game_uuid = await async_create_msc_game(game)
        if game_uuid:
            await message.reply(
                f"This game has been added to the Moonsea Codex, [click here to add it to your character log](https://moonseacodex.com/game/join/{game_uuid})",
                suppress=True,
            )
            return True
    return False
