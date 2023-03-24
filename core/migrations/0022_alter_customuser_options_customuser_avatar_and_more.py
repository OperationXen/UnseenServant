# Generated by Django 4.1.7 on 2023-03-18 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_dm_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Discord User', 'verbose_name_plural': 'Discord Users'},
        ),
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.URLField(blank=True, help_text='Path to the users avatar image', null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='discord_discriminator',
            field=models.CharField(blank=True, help_text='Discord discriminator number', max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='discord_id',
            field=models.PositiveBigIntegerField(blank=True, help_text='The discord ID number of the user', null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='ranks',
            field=models.ManyToManyField(help_text='Ranks held by this user (determined by roles)', related_name='users', to='core.rank'),
        ),
        migrations.AddField(
            model_name='rank',
            name='discord_id',
            field=models.BigIntegerField(blank=True, help_text='Discord role ID number', null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='discord_name',
            field=models.CharField(blank=True, help_text='User name and discriminator', max_length=64, null=True),
        ),
    ]