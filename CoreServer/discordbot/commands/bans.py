import discord
from discord import Embed, Colour, Message
from discord.ui import View

from discordbot.bot import bot
from core.utils.bans import get_outstanding_bans

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


class BannedPlayerEmbed(Embed):
    """ Custom embed for representing a player ban """
    ban_names = {'ST': 'Soft ban', 'HD': 'Hard ban', 'PM': 'Permanent ban'}
    ban_colours = {'ST': Colour.red(), 'HD': Colour.dark_red(), 'PM': Colour.light_grey()}

    def __init__(self, player, end, variant, issuer='', reason=''):
        super().__init__(title=player)
        self.add_field(name=self.ban_names[variant], value=f"Until: {end}", inline=False)
        if issuer or reason:
            self.add_field(name=f"Issued by {issuer}", value=reason, inline=False)
        self.color = self.ban_colours[variant]


@bot.command(name='ban_list2')
async def ban_list(ctx, arg: str = ""):
    """ show the list of banned players """
    embeds = []
    embeds.append(Embed(title='Banned players', colour=Colour.dark_purple()))

    if arg == 'all':
        await ctx.send(f"All banned players")
    else:
        current_bans = await get_outstanding_bans()
        for ban in current_bans:
            embeds.append(BannedPlayerEmbed(ban.discord_name, ban.datetime_end, ban.variant, ban.issued_by, ban.reason))

        await ctx.send(embeds=embeds)
