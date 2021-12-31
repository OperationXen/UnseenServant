from discordbot.bot import bot
from discord import Embed, Colour, Message
from core.utils.games import get_upcoming_games, get_player_list


class GameSummaryEmbed(Embed):
    """ Custom embed for summary of game """
    game_type_colours = {
        'RAL': Colour.green(), 'GAL': Colour.blue(), 'EAL': Colour.dark_green(),
        'NAL': Colour.orange(), 'CMP': Colour.dark_gold()}

    def __init__(self, game, players):
        super().__init__(title=game.name)
        self.color = self.game_type_colours[game.variant]
        
        self.add_field(name=game.module, value=f"{len(players)} / {game.max_players}")

@bot.command(name='games')
async def game_list(ctx, days: int = 30):
    """ show the list of upcoming games (optional days parameter) """
    embeds = []
    upcoming_games = await get_upcoming_games(days)
    embeds.append(Embed(title=f"Games in the next {days} days: [{len(upcoming_games)}]", colour=Colour.dark_purple()))

    for game in upcoming_games:
        players = await get_player_list(game)
        embeds.append(GameSummaryEmbed(game, players))
    await ctx.send(embeds=embeds)
