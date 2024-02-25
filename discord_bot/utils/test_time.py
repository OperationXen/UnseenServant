from datetime import datetime

from django.test import TestCase

from discord_bot.utils.time import *


class TestTimeUtils(TestCase):
    """tests for time utils"""

    def test_calculate_endtime(self):
        """sanity check the calculate_endtime function"""
        start_time = datetime.strptime("1970/01/01 00:00:00", "%Y/%m/%d %H:%M:%S")
        expected_end_time = datetime.strptime("1970/01/01 08:00:00", "%Y/%m/%d %H:%M:%S")
        end_time = calculate_endtime(start_time, 8)

        self.assertEqual(end_time, expected_end_time)
