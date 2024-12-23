# Generated by Django 5.1.1 on 2024-11-09 14:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_game_signup_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='tabletop',
            field=models.CharField(blank=True, help_text='Information about the tabletop that will be used, eg a link to a roll 20 room', max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='lottery',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lotteries', to='core.game'),
        ),
    ]
