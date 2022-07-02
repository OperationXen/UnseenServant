import platform
import logging

logger = logging.getLogger('discord-bot')
logger.setLevel(logging.DEBUG)

if platform.system() == 'Linux':
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
else:
    handler = logging.FileHandler('./invisible-servant.log')

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
