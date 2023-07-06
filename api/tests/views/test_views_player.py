import json
from copy import copy
from datetime import datetime, timedelta

from rest_framework.status import *
from django.test import TestCase
from django.urls import reverse

from core.models import Player


class TestPlayerViews(TestCase):
    """Check basic game CRUD functionality"""

    fixtures = ["test_games", "test_users", "test_dms", "test_players", "test_bans", "test_ranks"]

    valid_data = {}

    def test_get_single_player(self) -> None:
        """Anyone can retrive info about a single player"""
        self.client.logout()
        pass

    def test_list_players(self) -> None:
        """Check that a user can list players in games"""
        self.client.logout()
        pass

    def test_underpriv_user_cant_create_player(self) -> None:
        """Only the DM of a game or an admin can force add a player"""
        pass

    def test_dm_can_create_player(self) -> None:
        """A logged in DM user should be able to add a player to their game"""
        pass

    def test_underpriv_user_cant_edit_player(self) -> None:
        """DM or admin privs are required to edit player info"""
        pass

    def test_dm_can_edit_player(self) -> None:
        """A DM can edit a player in one of their own games"""
        pass

    def test_dm_cant_edit_all_players(self) -> None:
        """A DM can't edit players in other peoples games"""
        pass

    def test_underpriv_user_cant_delete_player(self) -> None:
        """Most players shouldn't be able to delete players"""
        pass

    def test_dm_can_delete_player(self) -> None:
        """A logged in DM should be able to remove a player from their own game"""
        pass
