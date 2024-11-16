import random

from discord import Embed, Colour


class BastionEmbed(Embed):
    """Embed to show details for a bastion turn"""

    def get_mercenary(self):
        return random.choice(
            [
                "Caswallon the fox",
                "Azeem the archer",
                "Fuzzbuzz the artificer",
                "Kenneth, son of Brian",
                "Brian, son of Kenneth",
                "Meepo the Magnificent",
                "Mirkandar the Magnificent",
                "Rondal",
                "Tyndal",
                "Lorcus",
            ]
        )

    def get_friendly_monster(self):
        return random.choice(
            [
                "Dryad",
                "Treant",
                "Flumph",
                "Brass dragon",
                "Gold dragon",
                "Silver dragon",
                "Copper dragon",
                "wandering tribe of kobolds",
            ]
        )

    def get_thumbnail_image(self):
        """randomly select a thumbnail image"""
        return random.choice(
            [
                # castles
                "https://i.pinimg.com/originals/7b/c0/5f/7bc05f6351db01f37422bbab9aa33c01.jpg",
                "https://i.pinimg.com/originals/ee/d2/9f/eed29ffc3e264605c89c489532b7e983.jpg",
                "https://i.pinimg.com/originals/35/66/4d/35664d534c71d2398fd7651851694877.jpg",
                "https://i.pinimg.com/originals/6f/1b/2c/6f1b2cdc0aa3856e580a41b4cc84f79e.jpg",
                "https://i.pinimg.com/originals/43/c5/fb/43c5fbe85672ea5abc0f497c01db5b1c.jpg",
                # towns
                "https://i.pinimg.com/originals/d9/bb/72/d9bb72a487c6529be8a7d2764f8758ba.jpg",
                "https://i.pinimg.com/originals/b0/dd/c2/b0ddc281550a6027f876e5c016c5922a.jpg",
                "https://i.pinimg.com/originals/19/68/b4/1968b4b3e8ff2b3da95b184af1ed9ca1.jpg",
                "https://i.pinimg.com/originals/23/1c/02/231c02cded02b2bf1fb83308988d29fc.jpg",
                "https://i.pinimg.com/originals/c8/bf/61/c8bf61133fc08f4ad013b18129865b01.jpg",
                "https://i.pinimg.com/originals/23/71/70/237170f9c073ab6824b0af9a4295d519.jpg",
                # caves
                "https://i.pinimg.com/originals/3c/57/84/3c578496f85aa23f91be77167eb83519.jpg",
                "https://i.pinimg.com/originals/1f/a2/6f/1fa26fab431aea26c4feaaeb3d87ce77.jpg",
                "https://cdnb.artstation.com/p/marketplace/presentation_assets/002/438/679/large/file.jpg",
                "https://cdnb.artstation.com/p/assets/images/images/062/150/743/large/illustranation-lebele-macro-photography-might-magic-fantasy-prison-lights-und-c3170d62-5fab-49e1-aa78-99ef18da694a-enhanced-sr.jpg",
                "https://i.pinimg.com/originals/45/3d/3f/453d3f5b467f4b60af4f4522955b1d54.jpg",
                # wizard towers
                "https://img.freepik.com/premium-photo/wizard-tower-fantasy-city-generative-ai_905627-227.jpg",
                "https://img.freepik.com/premium-photo/wizard-tower-fantasy-city-generative-ai_905627-226.jpg",
                "https://i.pinimg.com/originals/f2/83/55/f28355490e1390ec5b4ca22029726426.jpg",
                "https://i.pinimg.com/originals/11/97/af/1197af8d7296e5e1d322689051ac18df.jpg",
                "https://i.pinimg.com/originals/3c/48/25/3c48250b26fa426071c5a76d15689f79.jpg",
            ]
        )

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
                "Mirkandar the magnificent? Never heard of you mate, now sod off",
            ]
        )

    def attack(self):
        rolls = [random.randint(1, 6) for i in range(6)]
        message = f"A hostile force attacks your Bastion, but is defeated. "
        message += f"Roll 6D6: `{rolls}`; for each die that rolls a 1, one bastion defender is slain. "
        message += f"If the Bastion has zero defenders one of your special facilities (randomly picked) is damaged"
        return message

    def criminal_hireling(self):
        roll = random.randint(1, 6)
        message = "One of your hirelings has a criminal past which catches up with them. "
        message += f"You can keep the hireling at a cost of `{roll * 100}gp` in bribes, fines or to fund an elaborate and convoluted plan,"
        message += " otherwise the hireling is lost. If this leaves one of your facilities without hirelings that facility cannot be used on your next bastion turn, "
        message += " after which the hireling is replaced at no cost to you."
        message += "\nPossibly by someone wearing a very convincing fake moustache."
        return message

    def extraordinary_opportunity(self):
        message = (
            "Your bastion has a chance to hold a truely wonderful event, if you opt to seize this chance you must pay "
            "`500gp` in costs for food, drink, guards, spell components, replacement furniture, acrobats, repairs, costumes, etc. "
            "You may then roll again on the bastion events table, rerolling this event if it occurs again."
        )
        return message

    def friendly_visitors(self):
        roll = random.randint(1, 6)

        if random.randint(1, 100) > 90:
            message = f"A small group of bickering kobolds move into one of your facilities, creating a temporary shelter under a table in the corner. "
            message += f"Any attempts to move them on result in a tirade of angry swearing in draconic and what we can only assume are _very_ rude gestures. "
            message += f"As suddenly as they appear, they are gone, leaving `{roll * 100}gp` in a pile along with a badly written note thanking you for your hospitality."
        else:
            message = (
                f"A group of friendly visitors offer you `{roll * 100}gp` for the use of one of your facilities. "
            )
            message += "Mercifully they don't disrupt any ongoing work"
        return message

    def guest(self):
        roll = random.randint(1, 4)
        message = "Your bastion is visited by a friendly guest, "
        match roll:
            case 1:
                message += "an individual of great reknown who stays for a tenday. At the end of their stay they give you a `letter of recommendation`. "
                message += "possibly because they quite rudely just invited themselves to stay in your property."
            case 2:
                gift_roll = random.randint(1, 6)
                message += f"who is fleeing pursuit and requests sanctuary. After a tenday they depart, leaving you a gift of `{gift_roll * 100}gp`."
            case 3:
                message += f"a mercenary named {self.get_mercenary()}, who enjoys the bastion so much they ask to stay on as a bastion defender."
            case 4:
                message += f"a friendly {self.get_friendly_monster()}, who offers to stay and help defend your bastion in return for a place to rest. "
                message += "If your bastion is attacked whilst they are a guest the attack is repelled and you lose no defenders, after which your guest leaves."
        return message

    def lost_hireling(self):
        message = "One of facilities (chosen at random) loses all of its hirelings in what management have taken to calling 'the unpleasantness'. "
        message += "The facility can't be used on your next bastion turn, but replacements are found at no cost to you after that."
        return message

    def magical_discovery(self):
        message = "One of your hirelings creates or 'finds' an **Uncommon** magical scroll or potion of your choice."
        return message

    def refugees(self):
        refugee_rolls = [random.randint(1, 4) for i in range(2)]
        payment_roll = random.randint(1, 6)

        message = f"A group of `{sum(refugee_rolls)}` refugees fleeing calamity seek refuge at your bastion, camping outside if you cannot house them. "
        message += f"They offer you the choice of their meagre possessions in return for your aid, worth `{payment_roll * 100}gp`. "
        message += f"They stay until they find a new home or your bastion comes under attack."
        return message

    def request_for_aid(self):
        message = "Your bastion is called upon for aid by a local leader, to help you must dispatch a number of your bastion's defenders, "
        message += "for each that you send, roll a `D6`. If these rolls add up to 10 or more you solve the problem and receive `1D6 * 100 gp`. "
        message += "If you fail this roll, the reward is halved and one of your defenders is slain in the process."
        message += (
            "\n _Please note your choice below and make these rolls once you are committed using the `/roll` command_"
        )
        return message

    def treasure(self):
        roll = random.randint(1, 100)
        message = "A piece of treasure appears in your bastion, perhaps you've been blessed by the gods or simply lucky at cards. "
        message += f"Roll D100: `[{roll}]` - "

        if roll <= 40:
            message += "a piece of cheap art worth `25gp`."
        elif roll <= 63:
            message += "a piece of art worth `250gp`."
        elif roll <= 73:
            message += "a piece of fine art worth `750gp`."
        elif roll <= 75:
            message += "an incredible piece of art worth `2500gp`."
        elif roll < 90:
            message += (
                "A **Common** item from one of the following tables: `arcana`, `armaments`, `implements` or `relics`. "
            )
            message += "\n_Note your choice below and then roll a D100 using `/roll d100`_"
        elif roll < 98:
            message += "An **Uncommon** item from one of the following tables: `arcana`, `armaments`, `implements` or `relics`. "
            message += "\n_Note your choice below and then roll a D100 using `/roll d100`_"
        else:
            message += (
                "A **rare** item from one of the following tables: `arcana`, `armaments`, `implements` or `relics`. "
            )
            message += "\n_Note your choice below and then roll a D100 using `/roll d100`_"
        return message

    def bastion_events(self, roll: int):
        """get the name of the bastion event that has occured"""
        if roll <= 50:
            return {"name": "All is well", "value": self.all_is_well()}
        elif roll <= 55:
            return {"name": "Attack!", "value": self.attack()}
        elif roll <= 58:
            return {"name": "Criminal Hireling", "value": self.criminal_hireling()}
        elif roll <= 63:
            return {"name": "Extraordinary opportunity", "value": self.extraordinary_opportunity()}
        elif roll <= 72:
            return {"name": "Friendly visitors", "value": self.friendly_visitors()}
        elif roll <= 76:
            return {"name": "Guest", "value": self.guest()}
        elif roll <= 79:
            return {"name": "Lost hirelings", "value": self.lost_hireling()}
        elif roll <= 83:
            return {"name": "Magical Discovery", "value": self.magical_discovery()}
        elif roll <= 91:
            return {"name": "Refugees", "value": self.refugees()}
        elif roll <= 98:
            return {"name": "Request for aid", "value": self.request_for_aid()}
        else:
            return {"name": "Treasure", "value": self.treasure()}

    def __init__(self, username: str = "Someone", orders: str = ""):
        title = f"{username} takes a bastion turn"
        colour = Colour.dark_red()
        super().__init__(title=title, colour=colour)
        self.set_thumbnail(url=self.get_thumbnail_image())

        dice_result = random.randint(1, 100)
        event = self.bastion_events(dice_result)

        self.add_field(name="Bastion order: Maintain", value=f"Roll: [{dice_result}] - {event['name']}")
        self.add_field(name=event["name"], value=event["value"], inline=False)
