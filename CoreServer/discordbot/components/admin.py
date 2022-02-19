from discord import Embed, Colour

from discordbot.utils.format import documentation_url, admin_panel_url

class AdminUserCreatedEmbed(Embed):
    """ Embed to give a users who have successfully registered on the admin page """
    def __init__(self, username, password):
        title = f"Successfully registered as a DM with Unseen Servant"
        super().__init__(title=title, colour=Colour.purple())

        self.add_field(name='Credentials', value=f"Username: {username}\nPassword: {password}", inline=False)
        try:
            self.add_field(name='URL', value=f"<{admin_panel_url()}>", inline=False)
        except IndexError:
            self.add_field(name='URL', value=f"Please ask your server owner for the admin link", inline=False)
        self.add_field(name='Documentation', value=f"<{documentation_url()}>")
        self.add_field(name='Details', value='Please bookmark the above link, you can (and should) change your password on the admin page after logging in')
