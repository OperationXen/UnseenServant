from django.test import TestCase

from core.models import Game, Lottery, LotteryTicket, CustomUser


class ModelTestLottery(TestCase):
    """Test the lottery model"""

    fixtures = ["test_dms", "test_games", "test_users", "test_ranks"]

    def test_lottery_creation(self) -> None:
        """Test that a lottery can be created for a game"""
        game = Game.objects.get(pk=1)
        lottery = Lottery.objects.create(game=game)

        self.assertIsInstance(lottery, Lottery)

    # def test_lottery_unique_constraint(self) -> None:
    #     """Only one lottery can be created per game"""
    #     game = Game.objects.get(pk=1)

    #     with self.assertRaises(Exception):
    #         lottery_1 = Lottery.objects.create(game=game)
    #         lottery_2 = Lottery.objects.create(game=game)


class ModelTestLotteryTicket(TestCase):
    """Test the lottery ticket model"""

    fixtures = ["test_dms", "test_games", "test_users", "test_ranks", "test_lotteries"]

    def test_lottery_ticket_creation(self) -> None:
        """Check that we can create a lottery ticket"""
        test_lottery = Lottery.objects.get(pk=1)
        test_user = CustomUser.objects.get(pk=1)
        test_ticket = LotteryTicket.objects.create(lottery=test_lottery, user=test_user)

        self.assertIsInstance(test_ticket, LotteryTicket)
