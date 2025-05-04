from discord import Embed, Colour

from config.settings import MOONSEACODEX_URL


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
            value=f"[Link to item on Moonsea Codex]({MOONSEACODEX_URL}/magicitem/{item_uuid}/)",
            inline=False,
        )
