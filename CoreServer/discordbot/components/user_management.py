import discord
from discord import Embed, Colour, SelectOption
from discord.ui import View


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


class BanPlayerView(View):
    """ View for the player banning controls """
    def __init__(self, ctx, user, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.user = user
        self.reason = reason

    timeframe = 7
    length_1w = SelectOption(label='1 Week', value=7)
    length_2w = SelectOption(label='2 Weeks', value=14)
    length_1m = SelectOption(label='1 Month', value=30)
    length_2m = SelectOption(label='2 Months', value=60)
    length_3m = SelectOption(label='3 Months', value=90)
    forever = SelectOption(label='Permanent Ban', value=-1)

    @discord.ui.select(placeholder='Change ban length', row=0, options=[length_1w, length_2w, length_1m, length_2m, length_3m, forever])
    async def update_timescale(self, select, interaction):
        self.timeframe = int(select.values[0])
        if self.timeframe > 0:
            await interaction.response.edit_message(content=f"Banning player [{self.user}] for {self.timeframe} days\nReason: {self.reason}")
        else:
            await interaction.response.edit_message(content=f"Banning player [{self.user}] on a permanent basis\nReason: {self.reason}")

    @discord.ui.button(label="Soft ban", style=discord.ButtonStyle.primary, row=1)
    async def softban(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content=f"Banned player [{self.user}] from further signups for {self.timeframe} days", view=self)
    
    @discord.ui.button(label="Hard ban", style=discord.ButtonStyle.red, row=1)
    async def hardban(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(content=f"Banned player [{self.user}] for {self.timeframe} days, and removed them from all outstanding games", view=self)

    async def on_timeout(self):
        if self.message:
            await self.message.delete_original_message()
