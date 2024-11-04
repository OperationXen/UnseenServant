from discord import ButtonStyle
from discord.ui import View, Button

from discord_bot.components.moonseacodex import MSCCharacterList
from discord_bot.utils.moonseacodex import get_msc_characters
from core.utils.games import calc_game_tier
from core.utils.user import async_user_is_player_in_game, async_get_user_by_discord_id
from discord_bot.components.games import BaseGameEmbed
from discord_bot.utils.embed import async_update_game_embeds
from discord_bot.utils.players import async_do_waitlist_updates

from discord_bot.components.common import handle_player_dropout_event
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

    def __eq__(self, other):
        """Test this banner embed for equality with another"""
        if not other:
            return False
        if self.title != other.title:
            return False
        field_names = [field.name for field in self.fields]
        other_names = [field.name for field in other.fields]
        if set(field_names) != set(other_names):
            return False

        for field in self.fields:
            try:
                other_field = [x for x in other.fields if x.name == field.name][0]
                if field.value != other_field.value:
                    return False
            except Exception as e:
                return False
        return True

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
            return f"Greetings! Please submit the character you are bringing to this adventure at the earliest opportunity"

    async def build(self):
        """Get data from database and populate the embed"""
        await self.get_data()

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
        self.add_field(name="Content Warnings", value=f"{self.game.warnings[:1024] or 'None'}", inline=False)
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
        self.refresh_button = Button(
            style=ButtonStyle.grey, emoji="🔄", custom_id=f"unseen-servant-muster-refresh#{game.pk}"
        )
        self.dropout_button = Button(
            style=ButtonStyle.red, label="Drop out", custom_id=f"unseen-servant-muster-dropout#{game.pk}"
        )
        self.msc_button.callback = self.muster_view_msc
        self.refresh_button.callback = self.game_listing_view_refresh
        self.dropout_button.callback = self.muster_view_dropout

        self.add_item(self.msc_button)
        self.add_item(self.refresh_button)
        self.add_item(self.dropout_button)

    def get_existing_banner_by_title(self, title: str):
        """Get the mustering embed for this game by its title"""
        for embed in self.message.embeds:
            if embed.title == title:
                return embed

        # If no title match is found, fall back to the top one
        try:
            return self.message.embeds[0]
        except:
            return None

    def update_message_embeds(self, old_embed: MusteringBanner, new_embed: MusteringBanner) -> list[MusteringBanner]:
        """Find and replace the mustering embed within the message"""
        embeds = self.message.embeds
        index = embeds.index(old_embed)
        embeds[index] = new_embed
        return embeds

    async def update_message(self, followup_hook=None, response_hook=None):
        """Update the message this view is attached to"""
        updated_banner = MusteringBanner(self.game)
        await updated_banner.refresh_game_data()
        await updated_banner.build()
        existing_banner = self.get_existing_banner_by_title(updated_banner.title)
        if existing_banner != updated_banner:
            embeds = self.update_message_embeds(existing_banner, updated_banner)

            if followup_hook:
                await followup_hook.edit_message(message_id=self.message.id, embeds=embeds)
            elif response_hook:
                await response_hook.edit_message(embeds=embeds)
            else:
                await self.message.edit(embeds=embeds)
        else:
            return

    async def game_listing_view_refresh(self, interaction):
        """Force refresh button callback"""
        try:
            await interaction.response.defer(ephemeral=True)
            await async_do_waitlist_updates(self.game)
            await async_update_game_embeds(self.game)
        except Exception as e:
            log.error(f"[!] Error refreshing game from muster channel {self.game.name}: {e}")

    async def muster_view_dropout(self, interaction):
        """Callback for dropout button pressed"""
        try:
            await interaction.response.defer(ephemeral=True)
            await handle_player_dropout_event(self.game, interaction.user)
            await async_update_game_embeds(self.game)
        except Exception as e:
            log.error(f"f[!] Exception occured in drop interaction {e}")

    async def muster_view_msc(self, interaction):
        """Force refresh button callback"""
        await interaction.response.defer(ephemeral=True, invisible=False)

        user = await async_get_user_by_discord_id(interaction.user.id)
        if not await async_user_is_player_in_game(user, self.game):
            return await interaction.followup.send(f"You are on the waitlist", ephemeral=True, delete_after=10)

        discord_name = str(interaction.user.name)
        characters = get_msc_characters(discord_id=discord_name)
        if characters:
            view = MSCCharacterList(interaction.user, characters)
            view.message = await interaction.followup.send(
                f"Characters for discord user {discord_name} from the Moonsea Codex:", view=view, ephemeral=True
            )
        else:
            error_text = f"Cannot find any characters for you on Moonsea Codex, have you set your discord profile ID?"
            message = await interaction.followup.send(error_text, ephemeral=True)
