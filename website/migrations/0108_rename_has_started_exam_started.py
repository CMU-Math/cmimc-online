# Generated by Django 3.2.12 on 2022-02-19 01:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0107_auto_20220218_2039'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exam',
            old_name='has_started',
            new_name='started',
        ),
    ]
