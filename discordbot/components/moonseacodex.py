import discord
from discord import Embed, Colour, SelectOption
from discord.ui import View

class MSCCharacterEmbed(Embed):
    pass

class MSCCharacterList(View):
    """ View for retrieving and displaying a users characters from the MSC """
    character_list = []

    def __init__(self, ctx, characters):
        super().__init__()
        self.ctx = ctx
        for character in characters:
            x = SelectOption(label=f"{character.get('name')} ({character.get('race')})", value=character.get('uuid'))
            self.character_list.append(x)

    @discord.ui.select(placeholder='Pick a character', row=0, options=character_list)
    async def update_timescale(self, select, interaction):
        self.timeframe = int(select.values[0])
        if self.timeframe:
            await interaction.response.edit_message(content=f"Banning player [{self.user}] for {self.timeframe} days\nReason: {self.reason}")
        else:
            await interaction.response.edit_message(content=f"Banning player [{self.user}] on a permanent basis\nReason: {self.reason}")

    @discord.ui.button(label="Display", style=discord.ButtonStyle.primary, row=1)
    async def show_character(self, button, interaction):
        self.clear_items()
        if self.timeframe > 0:
            await interaction.response.edit_message(content=f"Banned player [{self.user}] from further signups for {self.timeframe} days", view=self)
        else:
            await interaction.response.edit_message(content=f"Banned player [{self.user}] from further signups", view=self)
