import platform
import logging

logger = logging.getLogger('discord-bot')
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('./database/discordbot.log')

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
