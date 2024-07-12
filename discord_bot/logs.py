import platform
import logging

logger = logging.getLogger("discord-bot")
logger.setLevel(logging.INFO)

try:
    handler = logging.FileHandler("./database/discordbot.log")
except Exception as e:
    handler = logging.FileHandler("./debugging.log")

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
