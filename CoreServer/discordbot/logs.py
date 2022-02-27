import logging 

logger = logging.getLogger('discord-bot')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('./unseen-servant.log')
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
