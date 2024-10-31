from asyncio import gather, create_task

from discord import Embed, Colour, ButtonStyle
from discord.ui import View, Button

import discord_bot.core
from discord_bot.logs import logger as log
from discord_bot.utils.players import async_do_waitlist_updates
from discord_bot.utils.time import discord_time, discord_countdown
from discord_bot.utils.embed import async_update_game_embeds
from discord_bot.utils.channel import async_add_discord_member_to_game_channel
from discord_bot.utils.format import generate_calendar_message
from discord_bot.utils.games import async_add_discord_member_to_game
from discord_bot.utils.messaging import async_send_dm
from core.models.game import Game
from core.errors import ChannelError
from core.utils.channels import async_get_game_channel_for_game
from core.errors import ChannelError
from core.utils.games import (
    async_get_player_list,
    async_get_wait_list,
    async_get_dm,
    is_patreon_exclusive,
    async_refetch_game_data,
    calc_game_tier,
)
from core.utils.players import async_get_player_credit_text, async_get_user_signups_remaining
from discord_bot.components.common import handle_player_dropout_event


class BaseGameEmbed(Embed):
    """Baseclass for game embed objects"""

    def __init__(self, game, title=None, colour=None):
        """Create an empty embed from a Game objected"""
        self.game = game
        if not colour:
            colour = self.game_type_colours[game.variant]
        if not title:
            title = game.name
        super().__init__(title=title, colour=colour)

    game_type_colours = {
        "Resident AL": Colour.blue(),
        "Guest AL DM": Colour.purple(),
        "Epic AL": Colour.dark_blue(),
        "Non-AL One Shot": Colour.orange(),
        "Campaign": Colour.dark_gold(),
    }

    async def refresh_game_data(self) -> Game:
        """Refresh the game object from the database"""
        self.game = await async_refetch_game_data(self.game)

    async def get_data(self):
        """Asyncronous wrapper to retrieve data from Django elements"""
        self.players = await async_get_player_list(self.game)
        self.waitlist = await async_get_wait_list(self.game)
        self.dm = await async_get_dm(self.game)

    def get_game_time(self):
        """Helper function to get the game time string"""
        time_info = f"{discord_time(self.game.datetime)} ({discord_countdown(self.game.datetime)})"
        if self.game.duration:
            time_info = time_info + f"\nDuration: {self.game.duration}"
        return time_info

    def waitlist_count(self):
        """Get number of players in waitlist"""
        return len(self.waitlist)

    def player_count(self):
        """Get number of confirmed players"""
        return len(self.players)


class GameSummaryEmbed(BaseGameEmbed):
    """Custom embed for summary view of game"""

    def __init__(self, game, colour=None):
        tier = calc_game_tier(game)
        if tier:
            title = f"{game.name} (T{tier})"
        else:
            title = f"{game.name}"
        super().__init__(game, title=title, colour=colour)

    def get_player_info(self):
        """get a string that shows current player status"""
        player_info = f"{self.player_count()} / {self.game.max_players} players"
        waitlisted = self.waitlist_count()
        if waitlisted:
            player_info = player_info + f"\n{waitlisted} in waitlist"
        else:
            player_info = player_info + "\nWaitlist empty"
        return player_info

    async def build(self):
        """Worker function that obtains data and populates the embed"""
        try:
            patreon_game = is_patreon_exclusive(self.game)
            await self.get_data()
            jump_url = discord_bot.core.game_controller.get_jump_url(self.game)
        except Exception as e:
            print(e)

        self.add_field(name="When", value=self.get_game_time(), inline=True)
        self.add_field(name="Players", value=self.get_player_info(), inline=True)
        description = f"{self.game.description[:76]} ..."
        self.add_field(name=f"{self.game.module}", value=description, inline=False)

        if patreon_game:
            if self.game.datetime_open_release:
                details = f"Release to general {discord_countdown(self.game.datetime_open_release)}\n"
            else:
                details = "This game is exclusive to patreons\n"
        else:
            details = "Game available for general signup\n"
        if jump_url:
            details = details + f"[Click here to view]({jump_url})"
        self.add_field(name="Game Details", value=details)


class GameDetailEmbed(BaseGameEmbed):
    """Embed for game detail view"""

    def __init__(self, game: Game):
        tier = calc_game_tier(game)
        if tier:
            title = f"{game.datetime.strftime('%Y/%m/%d')} {game.name} (T{tier})"
        else:
            title = f"{game.datetime.strftime('%Y/%m/%d')} {game.name}"
        super().__init__(game, title)
        self.game = game

    def __eq__(self, other):
        """Test this embed for equality with another"""
        if other == None:
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

    async def build(self):
        """Get data from database and populate the embed"""
        await self.get_data()
        try:
            dm_name = self.dm.name
        except:
            log.error(f"Unable to find DM entity for game {self.game.name}")
            dm_name = "Unknown DM"

        self.add_field(
            name=f"{self.game.module}",
            value=f"{self.game.description[:1024] or 'None'}",
            inline=False,
        )
        if self.game.realm != "Forgotten Realms":
            self.add_field(name="Setting", value=self.game.realm or "None", inline=False)

        self.add_field(name="When", value=self.get_game_time(), inline=True)

        self.add_field(
            name="Details",
            value=f"Character levels {self.game.level_min} - {self.game.level_max}\n DMed by {dm_name}",
            inline=True,
        )
        self.add_field(name="Game Type", value=f"{self.game.variant}", inline=True)
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
            self.add_field(name="Streaming", value=f"This game may be streamed")
        if self.game.play_test:
            self.add_field(name="Playtest", value=f"This game is a playtest")


class GameControlView(View):
    """View for game signup controls"""

    message = None

    def __init__(self, game):
        self.game = game
        super().__init__(timeout=None)
        # Creating these longhand instead of using the decorator because I need access to the game variable for unique custom IDs
        self.signup_button = Button(
            style=ButtonStyle.primary, label="Signup", custom_id=f"unseen-servant-signup#{game.pk}"
        )
        self.calendar_button = Button(
            style=ButtonStyle.grey, emoji="📆", custom_id=f"unseen-servant-calendar#{game.pk}"
        )
        self.refresh_button = Button(style=ButtonStyle.grey, emoji="🔄", custom_id=f"unseen-servant-refresh#{game.pk}")
        self.dropout_button = Button(
            style=ButtonStyle.red,
            label="Drop out",
            custom_id=f"unseen-servant-dropout#{game.pk}",
        )
        self.signup_button.callback = self.game_listing_view_signup
        self.calendar_button.callback = self.calendar
        self.refresh_button.callback = self.game_listing_view_refresh
        self.dropout_button.callback = self.game_listing_view_dropout
        self.add_item(self.signup_button)
        self.add_item(self.calendar_button)
        self.add_item(self.refresh_button)
        self.add_item(self.dropout_button)

    async def get_data(self):
        """retrieve data from Django (wrappers for syncronous calls)"""
        (self.players, self.dm) = await gather(async_get_player_list(self.game), async_get_dm(self.game))

    def get_existing_embed_by_title(self, title: str) -> GameDetailEmbed:
        """Get the embed for this game by its title"""
        for embed in self.message.embeds:
            if embed.title == title:
                return embed
        return None

    def update_message_embeds(self, old_embed: GameDetailEmbed, new_embed: GameDetailEmbed) -> list[GameDetailEmbed]:
        """Find and replace the game detail embed within the message"""
        embeds = self.message.embeds
        index = embeds.index(old_embed)
        if index is not None:
            embeds[index] = new_embed
        else:
            embeds.append(new_embed)
        return embeds

    async def update_message(self, followup_hook=None, response_hook=None):
        """Update the message this view is attached to"""
        detail_embed = GameDetailEmbed(self.game)
        await detail_embed.refresh_game_data()
        await detail_embed.build()

        existing_embed = self.get_existing_embed_by_title(detail_embed.title)
        if existing_embed != detail_embed:
            embeds = self.update_message_embeds(existing_embed, detail_embed)
            if followup_hook:
                return await followup_hook.edit_message(message_id=self.message.id, embeds=embeds)
            elif response_hook:
                return await response_hook.edit_message(embeds=embeds)
            else:
                return await self.message.edit(embeds=embeds)
        else:
            return

    async def game_listing_view_signup(self, interaction):
        """Callback for signup button pressed"""
        await interaction.response.defer(ephemeral=True)
        log.info(f"[>] User {interaction.user.name} signed up for game {self.game.name}")
        player = await async_add_discord_member_to_game(interaction.user, self.game)
        if not player:
            credits = await async_get_user_signups_remaining(interaction.user)
            await interaction.followup.send(
                f"Unable to add you to this game - {credits} signup credits available", ephemeral=True, delete_after=10
            )
            return False
        games_remaining_text = await async_get_player_credit_text(interaction.user)
        if not player.standby:
            try:
                channel = await async_get_game_channel_for_game(self.game)
                await async_add_discord_member_to_game_channel(interaction.user, channel)
            except ChannelError:
                pass  # no game channel exists, this is fine.
            message = f"You're playing in {self.game.name} `({games_remaining_text})`"
        else:
            message = f"Added you to to the waitlist for {self.game.name} `({games_remaining_text})`"
        await async_do_waitlist_updates(self.game)
        pending = []
        pending.append(create_task(async_update_game_embeds(self.game)))
        pending.append(create_task(async_send_dm(interaction.user, message)))
        await gather(*pending)
        return True

    async def calendar(self, interaction):
        """Calendar button callback"""
        await interaction.response.defer(ephemeral=True, invisible=False)
        message = generate_calendar_message(self.game)
        await interaction.followup.send(message, ephemeral=True, embeds=[])

    async def game_listing_view_dropout(self, interaction):
        """Callback for dropout button pressed"""
        try:
            await interaction.response.defer(ephemeral=True)
            await handle_player_dropout_event(self.game, interaction.user)
            await async_update_game_embeds(self.game)
        except Exception as e:
            log.error(f"f[!] Exception occured in drop interaction {e}")

    async def game_listing_view_refresh(self, interaction):
        """Force refresh button callback"""
        try:
            await interaction.response.defer(ephemeral=True)
            await async_do_waitlist_updates(self.game)
            await async_update_game_embeds(self.game)
        except Exception as e:
            log.error(f"[!] Error refreshing game {self.game.name}: {e}")
