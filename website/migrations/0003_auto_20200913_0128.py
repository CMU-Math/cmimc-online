# Generated by Django 3.1.1 on 2020-09-13 05:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20200913_0125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exam',
            old_name='show_grading_score',
            new_name='show_submission_scores',
        ),
    ]
