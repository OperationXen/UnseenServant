from discord import Message


def validate_game_log(message: Message) -> bool:
    """Check that the game log message looks reasonable"""
    if "### Game details" not in message.content:
        return False
    if "**Date:**" not in message.content:
        return False
    if "**Adventure:**" not in message.content:
        return False
    if "**Module Code:**" not in message.content:
        return False

    return True
