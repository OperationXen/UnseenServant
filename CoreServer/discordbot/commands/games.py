import discord
from discord import Embed, Colour
from discord.ui import View, button

from discordbot.bot import bot
from core.utils.games import get_upcoming_games, get_player_list, get_dm, get_specific_game


class GameEmbed(Embed):
    """ Baseclass for game embeds """
    game_type_colours = {
        'Resident AL': Colour.green(), 
        'Guest AL DM': Colour.blue(), 
        'Epic AL': Colour.dark_green(),
        'Non-AL One Shot': Colour.orange(), 
        'Campaign': Colour.dark_gold()
        }

    def get_game_time(self, game):
        time_info = f"<t:{int(game.datetime.timestamp())}:F>"
        if game.length:
            time_info = time_info + f"\nDuration: {game.length}"
        return time_info

    def get_player_info(self, game, players):
        player_info = f"{min(len(players), game.max_players)} / {game.max_players} players"
        if len(players) > game.max_players:
            player_info = player_info + f"\n{len(players) - game.max_players} in waitlist"
        else:
            player_info = player_info + "\nWaitlist empty"
        return player_info
    
    def get_player_details(self):
        pass


class GameSummaryEmbed(GameEmbed):
    """ Custom embed for summary of game """
    
    def __init__(self, game, players, dm):
        title = f"{game.variant} ({game.realm}) levels {game.level_min} - {game.level_max} by @{dm.name}"
        super().__init__(title=title, colour=self.game_type_colours[game.variant])

        self.add_field(name='When', value=self.get_game_time(game), inline=True)
        self.add_field(name='Players', value=self.get_player_info(game, players), inline=True)
        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description[:76]} ... ", inline=False)
        

class GameDetailEmbed(GameEmbed):
    """ Embed for game detail view """
    def __init__(self, game, players, dm):
        title = f"{game.variant} ({game.realm})"
        super().__init__(title = title, color=self.game_type_colours[game.variant])

        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description}", inline=False)
        self.add_field(name='When', value=self.get_game_time(game), inline=True)
        self.add_field(name='Details', value = f"Character levels {game.level_min} - {game.level_max}\n DMed by @{dm.name}", inline=True)
        self.add_field(name='Content Warnings', value=f"{game.warnings}", inline=False)
        self.add_field(name='Players', value=self.get_player_details(), inline=True)
        self.add_field(name='Waitlist', value="0", inline=True)
        
class GameControlView(View):
    """ View for game signup controls """
    def __init__(self, ctx):
        super().__init__(timeout=0)
        self.ctx = ctx

    @button(label="Signup", style=discord.ButtonStyle.primary, row=1)
    async def signup(self, button, interaction):
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
    await ctx.send(embed=GameDetailEmbed(game, players, dm), view=GameControlView(ctx))
