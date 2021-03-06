import discord
from discord import Embed, Colour, SelectOption
from discord.ui import View, Select

from discordbot.utils.moonseacodex import get_character_string, get_classes_string, get_stats_string, get_items_string


class MSCCharacterEmbed(Embed):
    """ Embed to display character details from MSC """
    tier_colours = {1: Colour.dark_green(), 2: Colour.dark_blue(), 3: Colour.dark_purple(), 4: Colour.dark_orange()}

    def get_tier(self, level):
        """ Calculates the character's tier """
        if level < 4:
            return 1
        elif level < 11:
            return 2
        elif level < 17:
            return 3
        return 4

    def get_equipped(self, items):
        """ Gets a list of equipped items """
        equipped = []
        for item in items:
            if item.get('equipped'):
                equipped.append(item)
        return equipped

    def __init__(self, character):
        super().__init__(title=get_character_string(character))
        level = character.get('level')
        sheet = character.get('sheet')
        tier = self.get_tier(level)
        self.multiclass = len(character.get('classes')) > 1
        equipped_items = self.get_equipped(character.get('items'))

        self.colour = self.tier_colours[tier]
        self.add_field(name='Classes' if self.multiclass else 'Class', value=get_classes_string(character), inline=False)
        self.add_field(name='Important Stats', value=get_stats_string(character), inline=True)
        self.add_field(name='Vision', value=f"{character.get('vision') or 'No special vision'}", inline=True)
        self.add_field(name=f"Equipped items ({len(equipped_items)})", value=get_items_string(equipped_items), inline=False)
        self.add_field(name='DM information', value=f"{character.get('dm_text') or 'No notable shenanigans'}", inline=False)
        self.add_field(name='Moonsea Codex', value=f"[Link to entry on Moonsea Codex](https://digitaldemiplane.com/moonseacodex/character/{character.get('uuid')}/)", inline=True)
        if sheet:
            self.add_field(name='Character sheet', value=f"[Link to character sheet]({sheet})", inline=True)
        if character.get('artwork'):
            self.set_thumbnail(url=f"https://digitaldemiplane.com{character.get('artwork')}")
        elif character.get('token'):
            self.set_thumbnail(url=f"https://digitaldemiplane.com{character.get('token')}")


class MSCCharacterList(View):
    """ View for retrieving and displaying a users characters from the MSC """
    characters = None
    character_picker = None

    def __init__(self, ctx, characters):
        super().__init__()
        self.ctx = ctx
        self.characters = characters

        character_list = []
        for character in characters:
            x = SelectOption(label=get_character_string(character), value=character.get('uuid'))
            character_list.append(x)
        self.character_picker = Select(options=character_list, placeholder='Character to post')
        self.character_picker.callback = self.pick_character
        self.add_item(self.character_picker)

    async def pick_character(self, interaction):
        for character in self.characters:
            if character.get('uuid') == self.character_picker.values[0]:
                embed = MSCCharacterEmbed(character)
                await interaction.channel.send(content=f"{self.ctx.author} presents a Moonsea Codex character", embed=embed)
                await interaction.response.edit_message(content=f"{character.get('name')} posted to channel", view=None, delete_after=5)
