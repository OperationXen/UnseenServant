from discord import Embed, Colour, ButtonStyle
from discord.ui import View, Button, button

from discordbot.utils.format import generate_calendar_message
from core.utils.games import get_player_list, get_wait_list, get_dm
from core.utils.games import add_player_to_game, drop_from_game
from core.utils.time import discord_time, discord_countdown

class BaseGameEmbed(Embed):
    """ Baseclass for game embed objects """

    def __init__(self, game, title = None, colour = None):
        """ Create an empty embed from a Game objected """
        self.game = game
        if not colour:
            colour = self.game_type_colours[game.variant]
        if not title:
            title = game.name
        super().__init__(title=title, colour=colour)

    game_type_colours = {
        'Resident AL': Colour.green(),
        'Guest AL DM': Colour.blue(),
        'Epic AL': Colour.dark_green(),
        'Non-AL One Shot': Colour.orange(),
        'Campaign': Colour.dark_gold()
        }

    async def get_data(self):
        """ Asyncronous wrapper to retrieve data from Django elements """
        self.players = await get_player_list(self.game)
        self.waitlist = await get_wait_list(self.game)
        self.dm = await get_dm(self.game)

    def get_game_time(self):
        """ Helper function to get the game time string """
        time_info = f"{discord_time(self.game.datetime)} ({discord_countdown(self.game.datetime)})"
        if self.game.length:
            time_info = time_info + f"\nDuration: {self.game.length}"
        return time_info

    def waitlist_count(self):
        """ Get number of players in waitlist """
        return len(self.waitlist)

    def player_count(self):
        """ Get number of confirmed players """
        return len(self.players)


class GameSummaryEmbed(BaseGameEmbed):
    """ Custom embed for summary view of game """

    def __init__(self, game, colour=None):
        title = f"{game.variant} ({game.realm}) levels {game.level_min} - {game.level_max}"
        super().__init__(game, title=title, colour=colour)

    def get_player_info(self):
        """ get a string that shows current player status """
        player_info = f"{self.player_count()} / {self.game.max_players} players"
        waitlisted = self.waitlist_count()
        if waitlisted:
            player_info = player_info + f"\n{waitlisted} in waitlist"
        else:
            player_info = player_info + "\nWaitlist empty"
        return player_info

    async def build(self): 
        """ Worker function that obtains data and populates the embed """
        await self.get_data()

        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Players', value=self.get_player_info(), inline=True)
        self.add_field(name=f"{self.game.module} | {self.game.name}", value=f"{self.game.description[:76]} ... ", inline=False)


class GameDetailEmbed(BaseGameEmbed):
    """ Embed for game detail view """

    def __init__(self, game):
        title = f"{game.variant} ({game.realm})"
        super().__init__(game, title)
        self.game = game

    def player_details_list(self):
        """ get list of all players with a spot in the game """
        player_list = '\n'.join(f"<@{p.discord_id}>" for p in self.players if not p.standby)
        return player_list or "None"

    def waitlist_details_list(self, max):
        """ get list of all players in waitlist """
        if not max:
            max = 8

        player_list = '\n'.join(f"<@{p.discord_id}>" for p in self.waitlist[:max])
        if len(self.waitlist) > max:
            player_list = player_list + f"\nand {len(self.waitlist) - max} more brave souls"
        return player_list or "None"

    async def build(self):
        """ Get data from database and populate the embed """
        await(self.get_data())

        self.add_field(name=f"{self.game.module} | {self.game.name}", value=f"{self.game.description}", inline=False)
        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Details', value = f"Character levels {self.game.level_min} - {self.game.level_max}\n DMed by <@{self.dm.discord_id}>", inline=True)
        self.add_field(name='Content Warnings', value=f"{self.game.warnings}", inline=False)
        self.add_field(name=f"Players ({self.player_count()} / {self.game.max_players})", value=self.player_details_list(), inline=True)
        self.add_field(name=f"Waitlist ({self.waitlist_count()})", value=self.waitlist_details_list(self.game.max_players), inline=True)
        if self.game.streaming:
            self.add_field(name='Streaming', value = f"This game may be streamed")


class GameControlView(View):
    """ View for game signup controls """
    message = None

    def __init__(self, game):
        self.game = game
        super().__init__(timeout=None)
        # Creating these longhand instead of using the decorator because I need access to the game variable for unique custom IDs
        self.signup_button = Button(style=ButtonStyle.primary, label='Signup', custom_id=f"unseen-servant-signup#{game.pk}")
        self.dropout_button = Button(style=ButtonStyle.red, label='Drop out', custom_id=f"unseen-servant-dropout#{game.pk}")
        self.calendar_button = Button(style=ButtonStyle.grey, label="Add to calendar", custom_id=f"unseen-servant-calendar#{game.pk}")
        self.signup_button.callback = self.signup
        self.dropout_button.callback = self.dropout
        self.calendar_button.callback = self.calendar
        self.add_item(self.signup_button)
        self.add_item(self.calendar_button)
        self.add_item(self.dropout_button)

    async def get_data(self):
        """ retrieve data from Django (syncronous) """
        self.players = await get_player_list(self.game)
        self.dm = await get_dm(self.game)

    async def update_message(self):
        """ Update the message this view is attached to """
        embeds = self.message.embeds
        detail_embed = GameDetailEmbed(self.game)
        await detail_embed.build()
        # Find and replace the game detail embed within the message by comparing titles
        for embed in embeds:
            if embed.title == detail_embed.title:
                index = embeds.index(embed)
                embeds[index] = detail_embed
        await self.message.edit(embeds = embeds)

    async def signup(self, interaction):
        status, message = await add_player_to_game(self.game, interaction.user)
        await interaction.response.send_message(message, ephemeral=True)
        if status == True:
            await self.update_message()

    async def calendar(self, interaction):
        message = generate_calendar_message(self.game)
        await interaction.response.send_message(message, ephemeral=True, embeds=[])

    async def dropout(self, interaction):
        status, message = await drop_from_game(self.game, interaction.user)
        await interaction.response.send_message(message, ephemeral=True)
        if status == True:
            await self.update_message()
