import discord
from discord.errors import NotFound
from discord import Embed, Colour, SelectOption
from discord.ui import View

from core.utils.players import issue_player_ban, get_outstanding_bans


class PlayerBanEmbed(Embed):
    """ Custom embed for representing a player ban """
    ban_names = {'ST': 'Soft ban - cannot sign up for new games', 'HD': 'Hard ban - removed from all games', 'PM': 'Permanent ban'}
    ban_colours = {'ST': Colour.red(), 'HD': Colour.dark_red(), 'PM': Colour.light_grey()}

    def __init__(self, ban):
        super().__init__(title=f"Ban: {ban.discord_name}")
        self.add_field(name='Ban details', value=self.ban_names[ban.variant], inline=False)
        if ban.datetime_end:
            self.add_field(name='Expiry', value=f"{ban.datetime_end.strftime('%Y/%m/%d %H:%M')}", inline=True)
        else:
            self.add_field(name='Expiry', value='Permenant ban', inline=True)
        if ban.issuer_name:
            self.add_field(name='Issued by', value=f"<@{ban.issuer_id}>", inline=True)
        if ban.reason:
            self.add_field(name='Reason', value=f"{ban.reason}", inline=False)
        self.colour = self.ban_colours[ban.variant]


class PlayerStrikeEmbed(Embed):
    """ Custom embed to represent a player strike """
    def __init__(self, strike):
        super().__init__(title=f"Strike: {strike.discord_name}")
        self.add_field(name='Expiry', value=f"{strike.expires.strftime('%Y/%m/%d %H:%M')}", inline=True)
        if strike.issuer_name:
            self.add_field(name='Issued by', value=f"<@{strike.issuer_id}>", inline=True)
        if strike.reason:
            self.add_field(name='Reason', value=f"{strike.reason}", inline=False)
        self.colour = Colour.yellow()


class BanPlayerView(View):
    """ View for the player banning controls """
    def __init__(self, ctx, user, reason):
        super().__init__(timeout=5)
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

    async def notify_user(self):
        """ Send a DM to the user to let them know """
        ban_list = []
        for ban in await get_outstanding_bans(self.user):
            ban_list.append(PlayerBanEmbed(ban))
        result = await self.user.send('You have been banned from using this bot', embeds=ban_list)

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
        await issue_player_ban(self.user, "ST", self.reason, self.ctx.author, self.timeframe)
        if self.timeframe > 0:
            await interaction.response.edit_message(content=f"Banned player [{self.user}] from further signups for {self.timeframe} days", view=self)
        else:
            await interaction.response.edit_message(content=f"Banned player [{self.user}] from further signups", view=self)
        await self.notify_user()
    
    @discord.ui.button(label="Hard ban", style=discord.ButtonStyle.red, row=1)
    async def hardban(self, button, interaction):
        self.clear_items()
        await issue_player_ban(self.user, "HD", self.reason, self.ctx.author, self.timeframe)
        if self.timeframe > 0:
            await interaction.response.edit_message(content=f"Banned player [{self.user}] for {self.timeframe} days, and removed them from all outstanding games", view=self)
        else:
            await interaction.response.edit_message(content=f"Banned player [{self.user}], and removed them from all outstanding games", view=self)
        await self.notify_user()

    async def on_timeout(self):
        """ When the view times out """
        print("View timed out")
        try:
            await self.message.delete_original_message()
        except NotFound:
            print(self.message)
