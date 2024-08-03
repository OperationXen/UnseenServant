import logging

logger = logging.getLogger("discord-bot")
logger.setLevel(logging.DEBUG)

try:
    handler = logging.FileHandler("./database/discordbot.log", encoding="utf8")
except Exception as e:
    handler = logging.FileHandler("./debugging.log", encoding="utf8")

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
