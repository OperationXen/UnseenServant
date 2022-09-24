# Generated by Django 4.1.1 on 2022-09-22 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_alter_game_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="GameChannel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "discord_id",
                    models.CharField(
                        blank=True,
                        help_text="Discord channel ID",
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "link",
                    models.URLField(
                        blank=True,
                        help_text="Link to the channel on discord",
                        null=True,
                    ),
                ),
                ("name", models.CharField(default="Unnamed game", max_length=64)),
                (
                    "status",
                    models.TextField(
                        choices=[
                            ("Ready", "Channel created"),
                            ("Reminder sent", "Members reminded of game"),
                            ("Warning sent", "1 Hour ping sent"),
                        ],
                        default="Ready",
                        help_text="Status of the channel",
                        max_length=32,
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="text_channel",
                        to="core.game",
                    ),
                ),
            ],
        ),
    ]