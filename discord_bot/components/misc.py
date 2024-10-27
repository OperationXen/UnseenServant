from discord import Embed, Colour

from discord_bot.utils.format import documentation_url


class HelpMessageEmbed(Embed):
    """Embed to hold a help message"""

    def __init__(self):
        super().__init__(title="Unseen Servant Usage Information", colour=Colour.lighter_gray())
        self.description = f"\n[Full User Guide here](<{documentation_url()}>)\n**Some commonly used commands:**"
        self.add_field(
            name="Signing up to games",
            value="Sign up and drop out from games using the buttons on listings in #patron-game-signups and #general-game-signups, or on [Tridengames.com](https://www.tridengames.com/calendar)",
            inline=False,
        )
        self.add_field(
            name="Player Commands",
            value="**/games** - lists the games you are signed up to: playing, waitlisted and DMing\n**/credit** - shows your remaining signup credit balance (also shown whenever you signup to / drop from a game)\n**/standing** - shows any strikes / bans in effect and their expiry",
            inline=False,
        )
        self.add_field(
            name="DM Commands",
            value="To create games, first assign yourself the Dungeon Master role from **#roles-and-rules**, the go to [Tridengames.com](https://www.tridengames.com/members). You will then be able to log in and create games.",
            inline=False,
        )
        self.add_field(
            name="Channel commands",
            value="\n5 days before game time, a new channel will be created only accessible by the DM and the players who will be tagged. Several useful commands are available to the DM inside a game channel:\n**/reset_channel_membership** - removes and re-adds players for this game. The first thing to try if a player cannot see the channel.\n**/tag_players** - will ping all players for this game.\n**/warn_waitlist** - sends a message with game details to the person at the top of the waitlist.\n**add_player** - immediately adds the specified player to game. This will force the game above the maximum number of players if full. The specified player will be removed from the waitlist if they were on it.\n**/remove_player** - immediately removes the specified player from the game. This can be useful if the player has advised they won’t be able to play but they haven’t pressed the button to drop out.",
            inline=False,
        )
