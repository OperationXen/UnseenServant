import json
from copy import copy
from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import Player


class TestGameActionViews(TestCase):
    """Check basic game CRUD functionality"""

    fixtures = ["test_games", "test_users", "test_dms", "test_players"]

    def test_anonymous_user_cant_join_game(self) -> None:
        """ Users must be logged in """
        pass

    def test_dm_cant_join_own_game(self) -> None:
        """ DMs cannot play in their own games """
        pass

    def test_credit_required_to_join_game(self) -> None:
        """ Players must have sufficient credit """
        pass

    def test_banned_user_cant_join(self) -> None:
        """ A banned user cannot join any games """
        pass

    def test_user_can_join_game(self) -> None:
        """ A user can join a game """
        pass

    def test_user_waitlisting(self) -> None:
        """ Players placed on waitlist if the game is full """
        pass

    def test_user_can_leave_game(self) -> None:
        """ Players leaving games are refunded their signup credit """
        pass

    def test_leave_game_error_message(self) -> None:
        """ An error message should be returned if you attempt to leave a game you are not in """
        pass
