from django.test import TestCase

from discord_bot.utils.moonseacodex import get_msc_characters


class APIUtilTests(TestCase):
    """ Test MSC API utilities """

    def test_fetch_character(self) -> None:
        """ can fetch a list of characters """
        response = get_msc_characters('')
        pass    # removed for now, because testing from github infra doesn't allow comms out
