from discord import Embed, Colour, ButtonStyle
from discord.ui import View, Button

import discordbot.core
from discordbot.logs import logger as log
from discordbot.utils.format import generate_calendar_message
from core.utils.games import get_player_list, get_wait_list, get_dm, get_game_by_id
from core.utils.games import add_player_to_game, drop_from_game, is_patreon_exclusive
from core.utils.players import get_player_credit_text
from discordbot.utils.time import discord_time, discord_countdown
from discordbot.utils.players import do_waitlist_updates

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
        'Resident AL': Colour.blue(),
        'Guest AL DM': Colour.purple(),
        'Epic AL': Colour.dark_blue(),
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
        try:
            patreon_game = is_patreon_exclusive(self.game)
            await self.get_data()
            jump_url = discordbot.core.game_controller.get_jump_url(self.game)
        except Exception as e:
            print (e)

        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Players', value=self.get_player_info(), inline=True)
        description = f"{self.game.description[:76]} ..."
        self.add_field(name=f"{self.game.module} | {self.game.name}", value = description, inline=False)

        if patreon_game:
            if self.game.datetime_open_release:
                details = f"Release to general {discord_countdown(self.game.datetime_open_release)}\n"
            else:
                details = 'This game is exclusive to patreons\n'
        else:
            details = 'Game available for general signup\n'
        if jump_url:
            details = details + f"[Click here to view]({jump_url})"
        self.add_field(name='Game Details', value=details)


class GameDetailEmbed(BaseGameEmbed):
    """ Embed for game detail view """
    def __init__(self, game):
        title = f"{game.variant} ({game.realm})"
        super().__init__(game, title)
        self.game = game

    def player_details_list(self):
        """ get list of all players with a spot in the game """
        player_list = '\n'.join(f"{p.discord_name}" for p in self.players if not p.standby)
        return player_list or "None"

    def waitlist_details_list(self, max):
        """ get list of all players in waitlist """
        if not max:
            max = 8
        if max < 3:
            max = 3

        player_list = '\n'.join(f"{p.discord_name}" for p in self.waitlist[:max])
        if len(self.waitlist) > max:
            player_list = player_list + f"\nand {len(self.waitlist) - max} more brave souls"
        return player_list or "None"

    async def build(self):
        """ Get data from database and populate the embed """
        await(self.get_data())

        self.add_field(name=f"{self.game.module} | {self.game.name}", value=f"{self.game.description[:1024] or 'None'}", inline=False)
        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Details', value = f"Character levels {self.game.level_min} - {self.game.level_max}\n DMed by {self.dm.discord_name}", inline=True)
        self.add_field(name='Content Warnings', value=f"{self.game.warnings or 'None'}", inline=False)
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
        self.calendar_button = Button(style=ButtonStyle.grey, emoji='????', custom_id=f"unseen-servant-calendar#{game.pk}")
        self.refresh_button = Button(style=ButtonStyle.grey, emoji= '????', custom_id=f"unseen-servant-refresh#{game.pk}")
        self.dropout_button = Button(style=ButtonStyle.red, label='Drop out', custom_id=f"unseen-servant-dropout#{game.pk}")
        self.signup_button.callback = self.signup
        self.calendar_button.callback = self.calendar
        self.refresh_button.callback = self.refresh
        self.dropout_button.callback = self.dropout
        self.add_item(self.signup_button)
        self.add_item(self.calendar_button)
        self.add_item(self.refresh_button)
        self.add_item(self.dropout_button)

    async def get_data(self):
        """ retrieve data from Django (syncronous) """
        self.players = await get_player_list(self.game)
        self.dm = await get_dm(self.game)

    async def update_message(self, followup_hook = None, response_hook = None):
        """ Update the message this view is attached to """
        embeds = self.message.embeds
        self.game = await get_game_by_id(self.game.id)
        detail_embed = GameDetailEmbed(self.game)
        await detail_embed.build()
        # Find and replace the game detail embed within the message by comparing titles
        for embed in embeds:
            if embed.title == detail_embed.title:
                index = embeds.index(embed)
                embeds[index] = detail_embed
        if followup_hook:
            await followup_hook.edit_message(message_id = self.message.id, embeds=embeds)
        elif response_hook:
            await response_hook.edit_message(embeds=embeds)
        else:
            await self.message.edit(embeds = embeds)

    async def signup(self, interaction):
        """ Callback for signup button pressed """
        status, message = await add_player_to_game(self.game, interaction.user)
        games_remaining_text = await get_player_credit_text(interaction.user)
        message = f"{message}\n{games_remaining_text}"
        await interaction.response.send_message(message, ephemeral=True, delete_after=30)
        log.info(f"Player {interaction.user.name} signed up for game {self.game.name}")
        await do_waitlist_updates(self.game)
        await self.update_message(followup_hook = interaction.followup)

    async def calendar(self, interaction):
        """ Calendar button callback """
        message = generate_calendar_message(self.game)
        await interaction.response.send_message(message, ephemeral=True, embeds=[])

    async def dropout(self, interaction):
        """ Callback for dropout button pressed """
        status, message = await drop_from_game(self.game, interaction.user)
        games_remaining_text = await get_player_credit_text(interaction.user)
        message = f"{message}\n{games_remaining_text}"
        await interaction.response.send_message(message, ephemeral=True, delete_after=30)
        log.info(f"Player {interaction.user.name} dropped from game {self.game.name}")
        await do_waitlist_updates(self.game)
        await self.update_message(followup_hook = interaction.followup)

    async def refresh(self, interaction):
        """ Force refresh button callback """
        # await interaction.response.send_message(f"Refreshing game view...", ephemeral=True, delete_after=5)
        await do_waitlist_updates(self.game)
        await self.update_message(response_hook = interaction.response)
