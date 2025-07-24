from discord.ext import tasks
from discord.utils import get

from config.settings import CHANNEL_SEND_PINGS
from discord_bot.logs import logger as log
from discord_bot.utils.time import get_hammertime, discord_countdown, discord_time
from discord_bot.utils.views import add_persistent_view
from discord_bot.utils.games import async_get_game_from_message, get_game_id_from_message
from discord_bot.utils.channel import async_create_channel_hidden
from discord_bot.utils.channel import async_get_all_game_channels_for_guild, async_get_channel_first_message
from discord_bot.components.channels import MusteringBanner, MusteringView
from core.utils.games import async_get_dm, async_get_player_list, async_get_wait_list
from core.utils.channels import async_get_games_pending_channel_creation, async_set_game_channel_created
from core.utils.channels import async_get_game_channels_pending_destruction, async_destroy_game_channel
from core.utils.channels import async_get_games_pending_channel_reminder, async_set_game_channel_reminded
from core.utils.channels import async_get_games_pending_channel_warning, async_set_game_channel_warned
from core.utils.channels import async_set_game_channel_summarised, async_get_games_pending_summary_post
from core.utils.channels import async_get_game_channel_for_game
from core.utils.channel_members import async_set_default_channel_membership
from core.utils.user import async_dm_is_res_dm, async_get_dm_user


class ChannelController:
    """Manager class for performing channel based functions"""

    initialised = False
    guild = None
    parent_category = None

    def __init__(self, guild):
        """initialisation function"""
        self.guild = guild
        self.channel_event_loop.start()

    async def get_topic_text(self, game):
        """build the game channel topic header"""
        dm = await async_get_dm(game)
        topic_text = "This thread is for mustering for the following game: "
        topic_text += f"{game.module} ({game.name}) | DMed by {dm.name} | "
        topic_text += f"Game is scheduled for {get_hammertime(game.datetime)}"
        return topic_text

    async def get_ping_text(self, game, include_waitlist=False):
        """Get text that will ping each of the users mentioned"""
        players = await async_get_player_list(game)
        dm = await async_get_dm(game)
        dm_user = await async_get_dm_user(dm)

        ping_text = f"- DM: <@{dm_user.discord_id}>"
        ping_text += "\n- Players: "
        ping_text += ",".join(f"<@{p.discord_id}>" for p in players)
        if include_waitlist:
            waitlist = await async_get_wait_list(game)
            ping_text += "\n- Waitlist: "
            ping_text += ",".join(f"<@{p.discord_id}>" for p in waitlist)
        return ping_text

    async def get_summary_text(self, game):
        """Build a summary text post"""
        players = await async_get_player_list(game)
        dm = await async_get_dm(game)
        dm_user = await async_get_dm_user(dm)
        is_res_dm = await async_dm_is_res_dm(dm)

        player_list = ",".join(f"<@{p.discord_id}>" for p in players)

        summary = "### Game details\n"
        summary += f"**Date:** {discord_time(game.datetime)}\n"
        summary += f"**Adventure:** {game.name}\n"
        summary += f"**Module Code:** {game.module}\n"
        summary += f"### Participants\n"
        summary += f"- **DM:** <@{dm_user.discord_id}>\n"
        if is_res_dm:
            summary += "- **Bonus Credit:** No\n"
        else:
            summary += "- **Bonus Credit:** Yes\n"
        summary += f"- **Players:** {player_list}\n"
        summary += f"### Rewards\n"
        summary += f"- **Item rewards**: \n"
        summary += f"- **Consumables found**: \n"
        summary += f"- **Gold per player**: \n"
        summary += f"- **Story awards**: \n"
        summary += f"-# You also receive 10 days of downtime and may take a level up"
        return f"```{summary}```"

    async def get_flat_message_list(self, game, include_waitlist=False):
        """Get a list of involved users, but in such a way as to not ping them"""
        players = await async_get_player_list(game)
        dm = await async_get_dm(game)
        dm_user = await async_get_dm_user(dm)

        text = f"- DM: {dm_user.discord_name}"
        text += "\n- Players: "
        text += ",".join(f"{p.discord_name}" for p in players if not p.standby)
        if include_waitlist:
            text += "\n- Waitlist: "
            text += ",".join(f"{p.discord_name}" for p in players if p.standby)
        return text

    async def send_banner_message(self, channel, game):
        """send the welcome banner"""
        try:
            control_view = MusteringView(game)
            banner = MusteringBanner(game)
            await banner.build()

            if CHANNEL_SEND_PINGS:
                ping_text = await self.get_ping_text(game)
                message = await channel.send(ping_text, embed=banner, view=control_view)
            else:
                flat_text = await self.get_flat_message_list(game)
                message = await channel.send(flat_text, embed=banner, view=control_view)
            control_view.message = message
            add_persistent_view(control_view)
            return True
        except Exception as e:
            log.error(f"Failed to send banner message to channel {channel.name}")
            return False

    async def check_and_create_channels(self):
        """Get outstanding channels needed and create them where missing"""
        pending_games = await async_get_games_pending_channel_creation()
        for upcoming_game in pending_games:
            log.info(f"[-] Creating channel for game: {upcoming_game.name}")
            channel_name = upcoming_game.datetime.strftime("%Y%m%d-") + upcoming_game.module
            channel_topic = await self.get_topic_text(upcoming_game)
            channel = await async_create_channel_hidden(self.guild, self.parent_category, channel_name, channel_topic)
            if channel:
                game_channel = await async_set_game_channel_created(
                    upcoming_game, channel.id, channel.jump_url, channel.name
                )
                await self.send_banner_message(channel, upcoming_game)
                log.debug(f"[-] GameChannel created OK")

                # now the channel has been created we can populate its membership list with the party
                set_members = await async_set_default_channel_membership(game_channel, True)
                if set_members:
                    log.debug(f"[-] Set channel membership list to default")

    async def check_and_delete_channels(self):
        """Go through any outstanding channels and delete anything older than 3 days"""
        try:
            expired_game_channels = await async_get_game_channels_pending_destruction()
            for game_channel in expired_game_channels:
                log.info(f"Removing game channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))
                if channel:
                    await channel.delete()
                else:
                    log.info("Cannot retrieve the expected discord channel, assuming its been deleted manually...")
                await async_destroy_game_channel(game_channel)
        except Exception as e:
            log.error(e)

    async def check_and_remind_channels(self):
        """Remind players 24 hours before their game"""
        try:
            upcoming_games = await async_get_games_pending_channel_reminder()
            for game in upcoming_games:
                game_channel = await async_get_game_channel_for_game(game)
                log.info(f"[-] Sending 24 hour reminder to channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))

                ping_text = await self.get_ping_text(game, include_waitlist=True)
                message = f"# Reminder: {game.name}\n"
                message += f"### This game is {discord_countdown(game.datetime)}\n"
                message += f"{ping_text}\n"

                message += (
                    "-# Please ensure that you have submitted all of the requested information if you are listed as a player"
                    " or you could be removed from the game.\n"
                    "-# If you are on the waitlist you do not need to do anything, **do not message the DM**. \n"
                    "-# Double check your availability for this game, no-showing the game may result in moderator action.\n"
                )
                await channel.send(message)
                await async_set_game_channel_reminded(game_channel)
        except Exception as e:
            log.error(f"[!] Exception in check_and_remind_channels: {e}")

    async def check_and_warn_channels(self):
        """Remind players 1 hour before their game"""
        try:
            upcoming_games = await async_get_games_pending_channel_warning()
            for game in upcoming_games:
                game_channel = await async_get_game_channel_for_game(game)
                log.info(f"[-] Sending 1 hour start warning to channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))

                ping_text = await self.get_ping_text(game)
                message = f"# {game.name} is starting {discord_countdown(game.datetime)}\n"
                message += f"{ping_text}\n"
                if game.tabletop:
                    # Putting links between < > prevents discord from creating an embed preview
                    message += f"### VTT info: <{game.tabletop}>\n"
                message += f"-# This is your last chance to submit your character information before you are removed from play, "
                message += f"please be ready in voice and VTT at least 5 minutes before the scheduled start."

                await channel.send(message)
                await async_set_game_channel_warned(game_channel)
        except Exception as e:
            log.error(f"[!] Exception in check_and_warn_channels: {e}")

    async def check_and_summarise_channels(self):
        """Print a summary of the game details suitable for session logs for the DM at game start"""
        try:
            games = await async_get_games_pending_summary_post()
            for game in games:
                game_channel = await async_get_game_channel_for_game(game)
                log.info(f"[-] Sending session log summary to channel: {game_channel.name}")
                channel = self.guild.get_channel(int(game_channel.discord_id))

                summary_text = await self.get_summary_text(game)
                await channel.send(summary_text)
                await async_set_game_channel_summarised(game_channel)
        except Exception as e:
            log.error(f"[!] Exception in check_and_summarise_channels: {e}")

    async def recover_channel_state(self):
        """Pull game postings from posting history and reconstruct a game/message status from it"""
        log.info("Reconnecting to existing mustering views")
        for channel in await async_get_all_game_channels_for_guild(self.guild):
            message = await async_get_channel_first_message(channel)
            game = await async_get_game_from_message(message)
            # Rebuild view handlers
            if game:
                control_view = MusteringView(game)
                control_view.message = message
                add_persistent_view(control_view)
                log.info(f"[+] Reconnected mustering view for {game.name}")
            elif message:
                game_id = get_game_id_from_message(message)
                log.error(
                    f"[!] Identified potentially ophaned mustering channel (no game to match) for game ID: {game_id}"
                )
            else:
                continue

    @tasks.loop(seconds=120)
    async def channel_event_loop(self):
        try:
            if not self.initialised:
                log.debug("[++] Starting up the Channel Controller loop")
                self.parent_category = get(self.guild.categories, name="Your Upcoming Games")
                await self.recover_channel_state()
                self.initialised = True

            await self.check_and_create_channels()
            await self.check_and_delete_channels()
            await self.check_and_summarise_channels()
            await self.check_and_warn_channels()
            await self.check_and_remind_channels()
        except Exception as e:
            log.error(f"[!] An unhandled exception has occured in the Channel Manager Loop: " + str(e))
            self.initialised = False
