from django.apps import AppConfig
from discordbot.logs import logger as log

class DiscordbotConfig(AppConfig):
	""" Configuration for the discord bot application """
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'discordbot'

	def ready(self):
		""" when app starts """
		pass
