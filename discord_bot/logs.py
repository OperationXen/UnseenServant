import logging
import sys

logger = logging.getLogger("discord-bot")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

try:
    file_handler = logging.FileHandler("./database/discordbot.log", encoding="utf8")
except Exception as e:
    file_handler = logging.FileHandler("./debugging.log", encoding="utf8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
