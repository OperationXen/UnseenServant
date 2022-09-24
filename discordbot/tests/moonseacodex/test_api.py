from django.test import TestCase

from discordbot.utils.moonseacodex import get_msc_characters


class APIUtilTests(TestCase):
    """ Test MSC API utilities """

    def test_fetch_character(self) -> None:
        """ can fetch a list of characters """
        response = get_msc_characters('')
        self.assertIsInstance(response, list)
        self.assertGreaterEqual(len(response), 0)
