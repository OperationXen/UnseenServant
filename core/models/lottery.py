from django.db import models

from core.models import Game, CustomUser


class Lottery(models.Model):
    """Defines an new lottery for seats at a game"""

    game = models.ForeignKey(Game, related_name="lotteries", on_delete=models.CASCADE, unique=True)
    cost = models.IntegerField(default=1, help_text="Credit cost of each ticket")
    ticket_limit = models.IntegerField(default=3, help_text="Max tickets per person")
    max_tickets = models.IntegerField(default=32, help_text="Total number of tickets available")

    datetime_open = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date/Time lottery tickets can be purchased",
        verbose_name="Lottery opening date/time",
    )
    datetime_draw = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date/Time lottery is closed and the winners are drawn",
        verbose_name="Lottery opening date/time",
    )
    draw_done = models.BooleanField(default=False)

    def __str__(self):
        retval = f"{self.game.name} - [{self.max_tickets}]"
        if self.draw_done:
            retval += " DRAWN"
        return retval


class LotteryTicket(models.Model):
    lottery = models.ForeignKey(Lottery, null=True, blank=True, related_name="tickets", on_delete=models.SET_NULL)
    user = models.ForeignKey(CustomUser, null=True, help_text="Owner of this lottery ticket", on_delete=models.CASCADE)
