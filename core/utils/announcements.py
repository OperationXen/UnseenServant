from typing import List
from asgiref.sync import sync_to_async
from random import choice as random_choice

from core.models import CustomUser, Announcement, GameChannelMember


def get_user_custom_announcements(user: CustomUser, waitlist: bool = False) -> List[Announcement]:
    """Get a list of all of a user's custom announcements"""
    announcements = user.announcements.all().filter(promotion=waitlist)
    return list(announcements)  # force evaluation here


def get_generic_announcements(waitlist: bool = False) -> List[Announcement]:
    """Get all of the generic announcements"""
    announcements = Announcement.objects.filter(generic=True).filter(promotion=waitlist)
    return list(announcements)  # force evaluation here


def generate_announcement_text(announcement: Announcement, user_text: str) -> str:
    """Combine an announcement and a user object"""
    text = announcement.text.replace("%u", user_text)
    return text


def get_player_announce_text(user: CustomUser, user_text: str, waitlist: bool = False) -> str:
    """
    Get an appropriate text string to use to announce the user
    Select randomly from custom lines if available, then randomly from generic lines
    """
    custom_announcements = get_user_custom_announcements(user, waitlist)
    generic_announcements = get_generic_announcements(waitlist)
    if custom_announcements:
        selected = random_choice(custom_announcements)
    elif generic_announcements:
        selected = random_choice(generic_announcements)
    else:
        return f"{user_text} joins the channel"
    text = generate_announcement_text(selected, user_text)
    return text


@sync_to_async
def async_get_player_announce_text(user: CustomUser, user_text: str, waitlist=False) -> str:
    """async wrapper to allow database access from async context"""
    return get_player_announce_text(user, user_text, waitlist)


# ##################################################################### #
def get_player_permissions_text(gcm: GameChannelMember, user_text: str):
    """get a string that shows what permissions are applied to a game channel member"""
    message = f"Channel permissions updated for {user_text}:"
    if gcm.send_messages:
        message += f"\n- :white_check_mark: Send messages"
    else:
        message += f"\n- :x: Send messages"
    if gcm.use_slash_commands and gcm.send_messages:
        message += f"\n- :white_check_mark: Use bot commands"
    else:
        message += f"\n- :x: Use bot commands"
    if gcm.manage_messages:
        message += f"\n- :white_check_mark: Channel moderator"
    return message
