import logging 

logger = logging.getLogger('discord-bot')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('./unseen-servant.log')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
