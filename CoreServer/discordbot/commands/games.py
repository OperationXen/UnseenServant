import discord
from asyncio import create_task as queue_async_task
from discord import Embed, Colour, ButtonStyle
from discord.ui import View, button, Button

from discordbot.bot import bot
from core.utils.games import get_upcoming_games, get_player_list, get_dm, get_specific_game


class GameEmbed(Embed):
    """ Baseclass for game embeds """
    def __init__(self, game, players, dm, title, colour=None):
        if not colour:
            colour = self.game_type_colours[game.variant]
        self.game = game
        self.players = players
        self.dm = dm
        super().__init__(title=title, colour=colour)

    game_type_colours = {
        'Resident AL': Colour.green(), 
        'Guest AL DM': Colour.blue(), 
        'Epic AL': Colour.dark_green(),
        'Non-AL One Shot': Colour.orange(), 
        'Campaign': Colour.dark_gold()
        }

    def get_game_time(self):
        time_info = f"<t:{int(self.game.datetime.timestamp())}:F>"
        if self.game.length:
            time_info = time_info + f"\nDuration: {self.game.length}"
        return time_info

    def get_waitlist_count(self):
        """ Get number of players in waitlist """
        waitlisted = sum(1 for p in self.players if p.standby)
        return waitlisted

    def get_player_count(self):
        """ Get number of confirmed players """
        player_count = sum(1 for p in self.players if not p.standby)
        return player_count

    def player_details_list(self):
        """ get list of all players with a spot in the game """
        player_list = '\n'.join(f"<@{p.discord_id}>" for p in self.players if not p.standby)
        return player_list

    def get_player_info(self):
        """ get a string that shows current player status """
        player_info = f"{self.get_player_count()} / {self.game.max_players} players"
        waitlisted = self.get_waitlist_count()
        if waitlisted:
            player_info = player_info + f"\n{waitlisted} in waitlist"
        else:
            player_info = player_info + "\nWaitlist empty"
        return player_info


class GameSummaryEmbed(GameEmbed):
    """ Custom embed for summary of game """
    
    def __init__(self, game, players, dm):
        title = f"{game.variant} ({game.realm}) levels {game.level_min} - {game.level_max} by {dm.name}"
        super().__init__(game, players, dm, title=title)

        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Players', value=self.get_player_info(), inline=True)
        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description[:76]} ... ", inline=False)


class GameDetailEmbed(GameEmbed):
    """ Embed for game detail view """

    def __init__(self, ctx, game, players, dm):
        title = f"{game.variant} ({game.realm})"
        super().__init__(game, players, dm, title = title)
        self.ctx = ctx

        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description}", inline=False)
        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Details', value = f"Character levels {game.level_min} - {game.level_max}\n DMed by <@{dm.discord_id}>", inline=True)
        self.add_field(name='Content Warnings', value=f"{game.warnings}", inline=False)
        self.add_field(name='Players', value=self.player_details_list(), inline=True)
        self.add_field(name='Waitlist', value=self.get_waitlist_count(), inline=True)


class GameControlView(View):
    """ View for game signup controls """
    def __init__(self, ctx, game):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.game = game

    @button(label='Signup', style=ButtonStyle.primary, custom_id='signup')
    async def signup(self, button, interaction):
        pass

    @button(label="Dropout", style=ButtonStyle.red, custom_id='dropout')
    async def dropout(self, button, interaction):
        pass


@bot.command(name='games')
async def game_list(ctx, days: int = 30):
    """ show the list of upcoming games (optional days parameter) """
    embeds = []
    upcoming_games = await get_upcoming_games(days)
    embeds.append(Embed(title=f"Games in the next {days} days: [{len(upcoming_games)}]", colour=Colour.dark_purple()))

    for game in upcoming_games:
        players = await get_player_list(game)
        dm = await get_dm(game)
        embeds.append(GameSummaryEmbed(game, players, dm))
    await ctx.send(embeds=embeds)

@bot.command(name='game')
async def game_details(ctx, game_id: int = 1):
    """ Get the details for a specific game """
    
    game = await get_specific_game(game_id)
    players = await get_player_list(game)
    dm = await get_dm(game)
    view = GameControlView(ctx, game)
    view.message = await ctx.send(embed=GameDetailEmbed(ctx, game, players, dm), view=view)
