from django.utils import timezone
from discord import Embed, Colour

from discordbot.components.games import BaseGameEmbed

class MusteringBanner(BaseGameEmbed):
    """ Banner announcing the game for the channel """
    def __init__(self, game):
        title = f"Mustering for ({game.module}) {game.name}"
        super().__init__(game, title)
        self.game = game

    def player_details_list(self):
        """ get list of all players with a spot in the game """
        player_list = '\n'.join(f"<@{p.discord_id}>" for p in self.players if not p.standby)
        return player_list or "None"

    def get_footer_text(self):
        """ mustering instructions """
        text = "Greetings! Please submit the character you are bringing to this adventure at the earliest opportunity"
        return text

    async def build(self):
        """ Get data from database and populate the embed """
        await(self.get_data())

        self.add_field(name=f"{self.game.module} | {self.game.name}", value=f"{self.game.description[:1024] or 'None'}", inline=False)
        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Details', value = f"Character levels {self.game.level_min} - {self.game.level_max}\n DMed by {self.dm.discord_name}", inline=True)
        self.add_field(name='Content Warnings', value=f"{self.game.warnings or 'None'}", inline=False)
        self.add_field(name=f"Players ({self.player_count()} / {self.game.max_players})", value=self.player_details_list(), inline=True)
        if self.game.streaming:
            self.add_field(name='Streaming', value = f"Reminder, this game may be streamed")
        self.set_footer(text=self.get_footer_text())


class MusteringView:
    """ View for mustering embed"""
    pass
