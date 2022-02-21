from discord import Embed, Colour

from discordbot.utils.format import documentation_url


class HelpMessageEmbed(Embed):
    """ Embed to hold a help message """
    def __init__(self):
        super().__init__(title='Unseen Servant Usage Information', colour=Colour.lighter_gray())
        self.description = f"\n[Full User Guide here](<{documentation_url()}>)\n**Some commonly used commands:**"
        self.add_field(name='Signing up to games', value='Sign up and drop out from games using the buttons on listings in #👑patron-game-signups and #🎲general-game-signups', inline=False)
        self.add_field(name='Player commands', value=
                        '**/games** - lists the games you are signed up to: playing, waitlisted and DMing\n\
                        **/games_summary** - lists upcoming games (can also be found in #📆game-calendar\n\
                        **/credit** - shows your remaining signup credit balance (also shown whenever you signup to / drop from a game)\n\
                        **/standing** - shows any strikes / bans in effect and their expiry', inline=False)
        self.add_field(name='DM Commands', value='**/register_as_dm** - gives you your initial login details for the portal where you can create games. As a DM you should definitely read the user guide which shows you how to do everything.', inline=False)
