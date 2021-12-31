import discord
from discord import Embed, Colour
from discord.ui import View

from discordbot.bot import bot
from core.utils.bans import get_outstanding_bans

ban_types = {'ST': 'Soft ban', 'HD': 'Hard ban', 'PM': 'Permanent ban'}


class BanPlayerView(View):
    def __init__(self, ctx, user):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.user = user

    timeframe = 7
    length_1w = discord.SelectOption(label='1 Week', value=7)
    length_2w = discord.SelectOption(label='2 Weeks', value=14)
    length_1m = discord.SelectOption(label='1 Month', value=30)
    length_2m = discord.SelectOption(label='2 Months', value=60)
    length_3m = discord.SelectOption(label='3 Months', value=90)
    forever = discord.SelectOption(label='Permanent Ban', value=-1)

    @discord.ui.select(placeholder='1 week', row=0, options=[length_1w, length_2w, length_1m, length_2m, length_3m, forever])
    async def update_timescale(self, select, interaction):
        self.timeframe = int(select.values[0])
        if self.timeframe > 0:
            await interaction.response.edit_message(content=f"Banning player [{self.user}] for {self.timeframe} days")
        else:
            await interaction.response.edit_message(content=f"Banning player [{self.user}] on a permanent basis")

    @discord.ui.button(label="Soft ban", style=discord.ButtonStyle.grey, row=1)
    async def softban(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content=f"Banned player [{self.user}] from further signups", view=self)
    
    @discord.ui.button(label="Hard ban", style=discord.ButtonStyle.grey, row=1)
    async def hardban(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content=f"Banned player [{self.user}], and removed them from all outstanding games", view=self)

    async def on_timeout(self):
        if self.message:
            await self.message.delete()

@bot.command(name='ban_player')
async def ban_player(ctx, user):
    view = view=BanPlayerView(ctx, user)
    view.message = await ctx.channel.send(f"Banning player {user}", view=view)

@bot.command(name='ban_list')
async def ban_list(ctx, arg: str = ""):
    if arg == 'all':
        await ctx.send(f"All banned players")
    else:
        current_bans = await get_outstanding_bans()
        banned_players = Embed(title='Banned Players', color=Colour.dark_red())
        for (player, end, variant, reason) in current_bans:
            banned_players.add_field(name=f"{player} until {end}", value=f"[{ban_types[variant]}] {reason}", inline=False)
        await ctx.send(embed=banned_players)
