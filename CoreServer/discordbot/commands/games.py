from discordbot.bot import bot
from discord import Embed, Colour, Message
from core.utils.games import get_upcoming_games, get_player_list, get_dm


class GameSummaryEmbed(Embed):
    """ Custom embed for summary of game """
    game_type_colours = {
        'RAL': Colour.green(), 'GAL': Colour.blue(), 'EAL': Colour.dark_green(),
        'NAL': Colour.orange(), 'CMP': Colour.dark_gold()}

    def __init__(self, game, players, dm):
        title = f"{game.variant} {game.realm} for levels {game.level_min} - {game.level_max} by {dm.name}"
        super().__init__(title=title, colour=self.game_type_colours[game.variant])
        
        self.add_field(name=f"{game.module} | {game.name}", value=f"{game.description}", inline=False)
        self.add_field(name='Details', value=f"Type: {game.variant}\nLevel range: {game.level_min} - {game.level_max}", inline=False)
        self.add_field(name='When', value=f"{game.datetime}\n{game.length} hours duration", inline=False)
        self.add_field(name='Players', value=f"{len(players)} / {game.max_players} players", inline=False)
        

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
