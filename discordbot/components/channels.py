from discord import ButtonStyle
from discord.ui import View, Button

from discordbot.components.moonseacodex import MSCCharacterList
from discordbot.utils.moonseacodex import get_msc_characters
from discordbot.utils.players import do_waitlist_updates
from core.utils.players import get_player_credit_text
from discordbot.components.games import BaseGameEmbed

from discordbot.utils.players import remove_player_from_game
from discordbot.logs import logger as log


class MusteringBanner(BaseGameEmbed):
    """Banner announcing the game for the channel"""

    def __init__(self, game):
        title = f"Mustering for ({game.module}) {game.name}"
        super().__init__(game, title)
        self.game = game

    def player_details_list(self):
        """get list of all players with a spot in the game"""
        player_list = "\n".join(f"<@{p.discord_id}>" for p in self.players if not p.standby)
        return player_list or "None"

    def get_muster_text(self):
        """mustering instructions"""
        if self.dm.muster_text:
            return self.dm.muster_text
        else:
            return (
                f"Greetings! Please submit the character you are bringing to this adventure at the earliest opportunity"
            )

    async def build(self):
        """Get data from database and populate the embed"""
        await (self.get_data())

        self.add_field(
            name=f"{self.game.module} | {self.game.name}",
            value=f"{self.game.description[:1024] or 'None'}",
            inline=False,
        )
        self.add_field(name="When", value=self.get_game_time(), inline=True)
        self.add_field(
            name="Details",
            value=f"Character levels {self.game.level_min} - {self.game.level_max}\n DMed by <@{self.dm.discord_id}>",
            inline=True,
        )
        self.add_field(name="Content Warnings", value=f"{self.game.warnings or 'None'}", inline=False)
        self.add_field(
            name=f"Players ({self.player_count()} / {self.game.max_players})",
            value=self.player_details_list(),
            inline=True,
        )
        if self.game.streaming:
            self.add_field(name="Streaming", value=f"Reminder, this game may be streamed")
        if self.dm.rules_text:
            self.add_field(name="DM Rules", value=self.dm.rules_text, inline=False)
        self.add_field(name="Instructions for players", value=self.get_muster_text(), inline=False)


class MusteringView(View):
    """View for mustering embed"""

    message = None

    def __init__(self, game):
        self.game = game
        super().__init__(timeout=None)
        # Creating these longhand instead of using the decorator because I need access to the game variable for unique custom IDs
        self.msc_button = Button(
            style=ButtonStyle.grey,
            emoji="📜",
            label="Import Character from Moonsea Codex",
            custom_id=f"unseen-servant-muster-import#{game.pk}",
        )
        self.dropout_button = Button(
            style=ButtonStyle.red, label="Drop out", custom_id=f"unseen-servant-muster-dropout#{game.pk}"
        )
        self.msc_button.callback = self.muster_view_msc
        self.dropout_button.callback = self.muster_view_dropout
        self.add_item(self.msc_button)
        self.add_item(self.dropout_button)

    async def update_message(self, followup_hook=None, response_hook=None):
        """Update the message this view is attached to"""
        embeds = self.message.embeds
        # self.game = await get_game_by_id(self.game.id)
        muster_banner = MusteringBanner(self.game)
        await muster_banner.build()
        # Find and replace the game detail embed within the message by comparing titles
        for embed in embeds:
            if embed.title == muster_banner.title:
                index = embeds.index(embed)
                embeds[index] = muster_banner
        if followup_hook:
            await followup_hook.edit_message(message_id=self.message.id, embeds=embeds)
        elif response_hook:
            await response_hook.edit_message(embeds=embeds)
        else:
            await self.message.edit(embeds=embeds)

    async def muster_view_dropout(self, interaction):
        """Callback for dropout button pressed"""
        message = await remove_player_from_game(self.game, interaction.user)
        games_remaining_text = await get_player_credit_text(interaction.user)
        message = f"{message}\n{games_remaining_text}"
        await interaction.response.send_message(message, ephemeral=True, delete_after=30)
        log.info(f"Player {interaction.user.name} dropped from game {self.game.name}")
        await do_waitlist_updates(self.game)
        await self.update_message(followup_hook=interaction.followup)

    async def muster_view_msc(self, interaction):
        """Force refresh button callback"""
        # await interaction.response.send_message(f"Refreshing game view...", ephemeral=True, delete_after=5)
        await interaction.response.defer(ephemeral=True)
        discord_id = str(interaction.user)
        characters = get_msc_characters(discord_id=discord_id)
        if characters:
            view = MSCCharacterList(interaction.user, characters)
            view.message = await interaction.followup.send(
                f"Characters for {interaction.user} from the Moonsea Codex:", view=view, ephemeral=True
            )
        else:
            message = await interaction.followup.send(
                f"Cannot find any characters for you on Moonsea Codex, have you set your discord profile ID?"
            )
