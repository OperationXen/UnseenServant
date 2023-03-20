from django.core.management.base import BaseCommand

from discord_bot.startup import start_bot

class Command(BaseCommand):
    help = 'Runs the unseen servant discord bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Unseen Servant'))
        try:
            start_bot()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception: {e}"))
        self.stdout.write(self.style.SUCCESS('Unseen Servant closing'))
