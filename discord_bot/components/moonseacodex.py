from discord import Embed, Colour, SelectOption
from discord.ui import View, Select

from discord_bot.logs import logger as log
from discord_bot.utils.moonseacodex import get_character_string, get_classes_string, get_stats_string, get_items_string


class MSCCharacterEmbed(Embed):
    """Embed to display character details from MSC"""

    tier_colours = {1: Colour.dark_green(), 2: Colour.dark_blue(), 3: Colour.dark_purple(), 4: Colour.dark_orange()}

    def get_tier(self, level):
        """Calculates the character's tier"""
        if level < 4:
            return 1
        elif level < 11:
            return 2
        elif level < 17:
            return 3
        return 4

    def get_equipped(self, items):
        """Gets a list of equipped items"""
        equipped = []
        for item in items:
            if item.get("equipped"):
                equipped.append(item)
        return equipped

    def get_dm_text(self, character):
        """Get the DM text, truncate if needed"""
        raw = character.get("dm_text")
        if not raw:
            return "No notable shenanigans"
        if len(raw) > 1024:
            return raw[:1020] + "..."
        return raw

    def get_links(self, character):
        """Get useful links for this character - MSC entry, char sheet, token download"""
        sheet = character.get("sheet")
        token = character.get("token")

        links = f"[MSC entry](https://digitaldemiplane.com/moonseacodex/character/{character.get('uuid')}/)"
        if sheet:
            links += f" | [Character sheet]({sheet})"
        if token:
            links += f" | [Token download](https://digitaldemiplane.com{token})"
        return links

    def __init__(self, character):
        try:
            super().__init__(title=get_character_string(character))
            level = character.get("level")
            tier = self.get_tier(level)
            self.multiclass = len(character.get("classes")) > 1
            equipped_items = self.get_equipped(character.get("items"))

            self.colour = self.tier_colours[tier]
            self.add_field(
                name="Classes" if self.multiclass else "Class", value=get_classes_string(character), inline=False
            )
            self.add_field(name="Important Stats", value=get_stats_string(character), inline=True)
            self.add_field(name="Vision", value=f"{character.get('vision') or 'No special vision'}", inline=True)
            self.add_field(
                name=f"Equipped items ({len(equipped_items)})", value=get_items_string(equipped_items), inline=False
            )
            self.add_field(name="DM information", value=self.get_dm_text(character), inline=False)

            self.add_field(name="Useful Links", value=self.get_links(character))

            if character.get("artwork"):
                self.set_thumbnail(url=f"https://digitaldemiplane.com{character.get('artwork')}")
            elif character.get("token"):
                self.set_thumbnail(url=f"https://digitaldemiplane.com{character.get('token')}")
        except Exception as e:
            log.error(f"Exception {str(e)} occured creating MSC embed for {character.get('name')}")


class MSCCharacterList(View):
    """View for retrieving and displaying a users characters from the MSC"""

    characters = None
    character_picker = None

    def __init__(self, user, characters):
        super().__init__()
        self.user = user
        self.characters = characters

        character_list = []
        for character in characters:
            x = SelectOption(label=get_character_string(character), value=character.get("uuid"))
            character_list.append(x)
        self.character_picker = Select(options=character_list, placeholder="Character to post")
        self.character_picker.callback = self.pick_character
        self.add_item(self.character_picker)

    async def pick_character(self, interaction):
        for character in self.characters:
            if character.get("uuid") == self.character_picker.values[0]:
                embed = MSCCharacterEmbed(character)
                await interaction.channel.send(
                    content=f"<@{self.user.id}> presents a Moonsea Codex character", embed=embed
                )
                await interaction.response.edit_message(
                    content=f"{character.get('name')} posted to channel", view=None, delete_after=5
                )


class MSCTradeSearchResultsEmbed(Embed):
    """Embed to display item advert details from MSC"""

    rarity_colours = {
        "uncommon": Colour.dark_green(),
        "rare": Colour.dark_blue(),
        "veryrare": Colour.dark_purple(),
        "legendary": Colour.dark_orange(),
    }

    def get_rarity_text(self, rarity):
        rarity_text = {"uncommon": "Uncommon", "rare": "Rare", "veryrare": "Very Rare", "legendary": "Legendary"}
        return rarity_text[rarity]

    def __init__(self, advert):
        item = advert.get("item")
        if not item:
            return
        name = item.get("name")
        rarity = item.get("rarity")
        owner = item.get("owner_name")
        item_uuid = item.get("uuid")
        description = advert.get("description")
        super().__init__(title=name)
        self.colour = self.rarity_colours[rarity]

        self.add_field(name="Rarity", value=self.get_rarity_text(rarity), inline=True)
        self.add_field(name="Owner", value=owner, inline=True)
        self.add_field(name="Desired trades", value=description, inline=False)
        self.add_field(
            name="Moonsea Codex",
            value=f"[Link to item on Moonsea Codex](https://digitaldemiplane.com/moonseacodex/magicitem/{item_uuid}/)",
            inline=False,
        )
