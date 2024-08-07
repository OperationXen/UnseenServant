from typing import List
from asgiref.sync import sync_to_async
from random import choice as random_choice

from core.models import CustomUser, Announcement


def get_user_custom_announcements(user: CustomUser) -> List[Announcement]:
    """Get a list of all of a user's custom announcements"""
    announcements = user.announcements.all()
    return list(announcements)  # force evaluation here


def get_generic_announcements() -> List[Announcement]:
    """Get all of the generic announcements"""
    announcements = Announcement.objects.filter(generic=True)
    return list(announcements)  # force evaluation here


def generate_announcement_text(announcement: Announcement, user_text: str) -> str:
    """Combine an announcement and a user object"""
    text = announcement.text.replace("%u", user_text)
    return text


def get_player_announce_text(user: CustomUser, user_text: str) -> str:
    """
    Get an appropriate text string to use to announce the user
    Select randomly from custom lines if available, then randomly from generic lines
    """
    custom_announcements = get_user_custom_announcements(user)
    generic_announcements = get_generic_announcements()
    if custom_announcements:
        selected = random_choice(custom_announcements)
    elif generic_announcements:
        selected = random_choice(generic_announcements)
    else:
        return f"{user_text} joins the channel"
    text = generate_announcement_text(selected, user_text)
    return text


@sync_to_async
def async_get_player_announce_text(user: CustomUser, user_text: str) -> str:
    """async wrapper to allow database access from async context"""
    return get_player_announce_text(user, user_text)
