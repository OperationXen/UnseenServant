import discord
from asyncio import create_task as queue_async_task
from discord import Embed, Colour, ButtonStyle
from discord.ui import View, button, Button

from discordbot.bot import bot
from discordbot.utils.format import generate_calendar_message
from core.utils.games import get_upcoming_games, get_player_list, get_dm, get_specific_game
from core.utils.games import add_player_to_game, remove_player_from_game
from core.utils.games import get_waitlist


class GameEmbed(Embed):
    """ Baseclass for game embeds """
    def __init__(self, game, players, waitlist, dm, title, colour=None):
        if not colour:
            colour = self.game_type_colours[game.variant]
        self.game = game
        self.players = players
        self.waitlist = waitlist
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
        return len(self.waitlist)

    def get_player_count(self):
        """ Get number of confirmed players """
        player_count = sum(1 for p in self.players if not p.standby)
        return player_count

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
        super().__init__(game, players, [], dm, title=title)

        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Players', value=self.get_player_info(), inline=True)
        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description[:76]} ... ", inline=False)


class GameDetailEmbed(GameEmbed):
    """ Embed for game detail view """

    def __init__(self, game, players, waitlist, dm):
        title = f"{game.variant} ({game.realm})"
        super().__init__(game, players, waitlist, dm, title = title)

        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description}", inline=False)
        self.add_field(name='When', value=self.get_game_time(), inline=True)
        self.add_field(name='Details', value = f"Character levels {game.level_min} - {game.level_max}\n DMed by <@{dm.discord_id}>", inline=True)
        self.add_field(name='Content Warnings', value=f"{game.warnings}", inline=False)
        self.add_field(name=f"Players ({self.get_player_count()} / {self.game.max_players})", value=self.player_details_list(), inline=True)
        self.add_field(name=f"Waitlist ({self.get_waitlist_count()})", value=self.waitlist_details_list(self.game.max_players), inline=True)


class GameControlView(View):
    """ View for game signup controls """
    def __init__(self, game, players, dm):
        super().__init__(timeout=None)
        self.game = game
        self.players = players
        self.dm = dm

    @button(label='Signup', style=ButtonStyle.primary, custom_id='signup')
    async def signup(self, button, interaction):
        status, message = await add_player_to_game(self.game, interaction.user)
        await interaction.response.send_message(message, ephemeral=True)
        if status == True:
            new_players = await get_player_list(self.game)
            new_waitlist = await get_waitlist(self.game)
            await self.message.edit(embed = GameDetailEmbed(self.game, new_players, new_waitlist, self.dm))

    @button(label='Add to calendar', style=ButtonStyle.grey)
    async def calendar(self, button, interaction):
        message = generate_calendar_message(self.game)
        await interaction.response.send_message(message, ephemeral=True, embeds=[])

    @button(label="Dropout", style=ButtonStyle.red, custom_id='dropout')
    async def dropout(self, button, interaction):
        status, message = await remove_player_from_game(self.game, interaction.user)
        await interaction.response.send_message(message, ephemeral=True)
        if status == True:
            new_players = await get_player_list(self.game)
            new_waitlist = await get_waitlist(self.game)
            await self.message.edit(embed = GameDetailEmbed(self.game, new_players, new_waitlist, self.dm))


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
    if game:
        players = await get_player_list(game)
        waitlist = await get_waitlist(game)
        dm = await get_dm(game)
        view = GameControlView(game, players, dm)
        view.message = await ctx.send(embed=GameDetailEmbed(game, players, waitlist, dm), view=view)
    else:
        await ctx.send('No game found')
