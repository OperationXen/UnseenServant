from discord import ButtonStyle
from discord.ui import View, Button

from discord_bot.components.moonseacodex import MSCCharacterList
from discord_bot.utils.moonseacodex import get_msc_characters
from discord_bot.utils.players import do_waitlist_updates
from core.utils.players import get_player_credit_text
from core.utils.games import calc_game_tier
from discord_bot.components.games import BaseGameEmbed

from discord_bot.utils.players import remove_player_from_game
from discord_bot.utils.games import update_game_listing_embed
from discord_bot.logs import logger as log


class MusteringBanner(BaseGameEmbed):
    """Banner announcing the game for the channel"""

    def __init__(self, game):
        tier = calc_game_tier(game)
        if tier:
            title = f"Mustering for {game.name} (T{tier})"
        else:
            title = f"Mustering for {game.name}"
        super().__init__(game, title)
        self.game = game

    def player_details_list(self):
        """get list of all players with a spot in the game"""
        player_list = "\n".join(f"{p.discord_name}" for p in self.players if not p.standby)
        return player_list or "None"

    def waitlist_details_list(self, max):
        """get list of all players in waitlist"""
        if not max:
            max = 8
        if max < 3:
            max = 3

        player_list = "\n".join(f"{p.discord_name}" for p in self.waitlist[:max])
        if len(self.waitlist) > max:
            player_list = player_list + f"\nand {len(self.waitlist) - max} more brave souls"
        return player_list or "None"

    def get_muster_text(self):
        """mustering instructions"""
        if self.dm.muster_text:
            return self.dm.muster_text[:1024]
        else:
            return (
                f"Greetings! Please submit the character you are bringing to this adventure at the earliest opportunity"
            )

    async def build(self):
        """Get data from database and populate the embed"""
        await (self.get_data())

        self.add_field(
            name=f"{self.game.module}",
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
        self.add_field(
            name=f"Waitlist ({self.waitlist_count()})",
            value=self.waitlist_details_list(self.game.max_players),
            inline=True,
        )
        if self.game.streaming:
            self.add_field(name="Streaming", value=f"Reminder, this game may be streamed")
        if self.dm.rules_text:
            self.add_field(name="DM Rules", value=self.dm.rules_text[:1024], inline=False)
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

    def update_message_embeds(self, new_embed: MusteringBanner) -> list[MusteringBanner]:
        """ Find and replace the mustering embed within the message """
        embeds = self.message.embeds
        if len(embeds) <= 1:                                # If there's only one (or none) embed, replace it
            embeds[0] = new_embed
        else:
            for embed in embeds:                            # Otherwise we need to look for a match by comparing titles
                if embed.title == new_embed.title:
                    index = embeds.index(embed)
                    embeds[index] = new_embed
        return embeds


    async def update_message(self, followup_hook=None, response_hook=None):
        """Update the message this view is attached to"""
        muster_banner = MusteringBanner(self.game)
        await muster_banner.build()
        embeds = self.update_message_embeds(muster_banner)

        if followup_hook:
            await followup_hook.edit_message(message_id=self.message.id, embeds=embeds)
        elif response_hook:
            await response_hook.edit_message(embeds=embeds)
        else:
            await self.message.edit(embeds=embeds)

    async def muster_view_dropout(self, interaction):
        """Callback for dropout button pressed"""
        await interaction.response.defer(ephemeral=True)
        removed = await remove_player_from_game(self.game, interaction.user)
        if removed:
            log.info(f"Player {interaction.user.name} dropped from game {self.game.name}")
            games_remaining_text = await get_player_credit_text(interaction.user)
            message = f"Removed you from {self.game.name} `({games_remaining_text})`"
            await do_waitlist_updates(self.game)
            await self.update_message(followup_hook=interaction.followup)
            await update_game_listing_embed(self.game)
            await interaction.user.send(message)
            return True
        await interaction.followup.send('Unable to remove you from this game, please consult the fates. It would appear to be your destiny.', ephemeral=True)
        return False

    async def muster_view_msc(self, interaction):
        """Force refresh button callback"""
        await interaction.response.defer(ephemeral=True, invisible=False)
        discord_name = str(interaction.user)
        characters = get_msc_characters(discord_id=discord_name)
        if characters:
            view = MSCCharacterList(interaction.user, characters)
            view.message = await interaction.followup.send(f"Characters for {discord_name} from the Moonsea Codex:", view=view, ephemeral=True)
        else:
            error_text = f"Cannot find any characters for you on Moonsea Codex, have you set your discord profile ID?"
            message = await interaction.followup.send(error_text, ephemeral=True)
