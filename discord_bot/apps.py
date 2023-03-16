from django.apps import AppConfig
from discord_bot.logs import logger as log

class DiscordbotConfig(AppConfig):
	""" Configuration for the discord bot application """
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'discord_bot'

	def ready(self):
		""" when app starts """
		pass
