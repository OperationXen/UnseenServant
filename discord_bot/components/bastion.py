import random

from discord import Embed, Colour


class BastionEmbed(Embed):
    """Embed to show details for a bastion turn"""

    def all_is_well(self):
        """Generate a random innocuous event"""
        return random.choice(
            [
                "Giant rats living in the sewers beneath our feet? Preposterous.",
                "If you build walls under the castle to keep out the mines; and walls above the castle to keep out the giants and flying creatures, then you might have a safe castle. Exept for magic. And running out of food.",
                "Good news my liege! Accident reports are down this tenday.",
                "I have excellent news, the leak in the roof above your bed has been fixed",
                "I want to make this abundantly clear, there are no giant rat infestations to report.",
                "Unfortunately someone has lost their spectacles again and we've all been looking for them. For days.",
                "One of the staff has adopted a stray dog, and everyone has been too busy playing with it to do any work",
                "A friend has sent you a letter. I promise nobody read it.",
                "Someone started a practical joke war, and it's starting to get a little out of hand",
                "I don't want to panic you, in fact I want you to remain perfectly calm. It's entirely possible that there well be a ghost... somewhere.",
                "All kobold sightings must be reported to management, _do not_ attempt to domesticate them.",
                "A group of halflings attempted to pass through with an obviously stolen ring of invisibility",
                "One of the staff reports hearing a high-pitched argument coming from underground, it's probably nothing",
                "The more important the man, the sillier the hat.",
                "A mercenary wizard named Caswallon stopped by looking for work",
                "Mirkandar the magnificent? Never heard of you mate, now sod off",
            ]
        )

    def bastion_events(self, roll: int):
        """get the name of the bastion event that has occured"""
        if roll <= 50:
            return {"name": "All is well", "value": self.all_is_well()}
        elif roll <= 55:
            return {"name": "Attack!", "value": ""}
        elif roll <= 58:
            return {"name": "Criminal Hireling", "value": ""}
        elif roll <= 63:
            return {"name": "Extraordinary opportunity", "value": ""}
        elif roll <= 72:
            return {"name": "Friendly visitors", "value": ""}
        elif roll <= 76:
            return {"name": "Guest", "value": ""}
        elif roll <= 79:
            return {"name": "Lost hirelings", "value": ""}
        elif roll <= 83:
            return {"name": "Magical Discovery", "value": ""}
        elif roll <= 91:
            return {"name": "Refugees", "value": ""}
        elif roll <= 98:
            return {"name": "Request for aid", "value": ""}
        else:
            return {"name": "Treasure", "value": ""}

    def __init__(self, username: str = "Someone", orders: str = ""):
        title = f"{username} takes a bastion turn"
        colour = Colour.dark_red()
        super().__init__(title=title, colour=colour)

        dice_result = random.randint(1, 100)
        event = self.bastion_events(dice_result)

        self.add_field(name="Bastion order: Maintain", value=f"Roll: [{dice_result}] - {event['name']}")
        self.add_field(name=event["name"], value=event["value"], inline=False)
