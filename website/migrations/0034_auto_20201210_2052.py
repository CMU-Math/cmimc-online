# Generated by Django 3.1.3 on 2020-12-11 01:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0033_auto_20201210_2045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='show_leaderboard',
        ),
        migrations.RemoveField(
            model_name='exam',
            name='show_own_scores',
        ),
    ]