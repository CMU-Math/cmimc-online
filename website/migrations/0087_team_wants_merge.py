# Generated by Django 3.1.6 on 2021-02-19 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0086_divchoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='wants_merge',
            field=models.BooleanField(default=False),
        ),
    ]
