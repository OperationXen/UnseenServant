# Generated by Django 4.0 on 2022-01-07 20:02

import core.utils.time
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='User friendly name for this rank', max_length=32)),
                ('priority', models.IntegerField(help_text='The relative seniority of this rank compared to others (higher = more senior)')),
                ('max_games', models.IntegerField(default=0, help_text='Upper limit for games members of this rank are allowed to join')),
                ('patreon', models.BooleanField(default=False, help_text='this rank is reserved for paying members')),
            ],
        ),
        migrations.CreateModel(
            name='Strike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.IntegerField(blank=True, help_text='Discord ID of player', null=True)),
                ('discord_name', models.CharField(blank=True, help_text='Banned player name', max_length=32)),
                ('datetime', models.DateTimeField(auto_now_add=True, help_text='Strike issued')),
                ('expires', models.DateTimeField(default=core.utils.time.a_year_from_now, help_text='Strike expiry date/time')),
                ('issued_by', models.CharField(help_text='Name of the issuing admin', max_length=32)),
                ('reason', models.TextField(help_text='Reason for issuing the strike')),
            ],
        ),
        migrations.AlterModelOptions(
            name='dm',
            options={'verbose_name': 'DM', 'verbose_name_plural': 'DMs'},
        ),
        migrations.AlterField(
            model_name='ban',
            name='datetime_end',
            field=models.DateTimeField(default=core.utils.time.a_month_from_now, help_text='Ban expiry date/time'),
        ),
        migrations.AlterField(
            model_name='ban',
            name='datetime_start',
            field=models.DateTimeField(auto_now_add=True, help_text='Ban start date/time'),
        ),
        migrations.AlterField(
            model_name='ban',
            name='reason',
            field=models.TextField(help_text='Reason for the ban to be issued'),
        ),
        migrations.AlterField(
            model_name='dm',
            name='description',
            field=models.TextField(blank=True, help_text='Flavour text / details to show'),
        ),
        migrations.AlterField(
            model_name='game',
            name='warnings',
            field=models.TextField(default='None', help_text='Content warnings or advisories'),
        ),
    ]