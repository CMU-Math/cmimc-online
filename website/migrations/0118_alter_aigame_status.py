# Generated by Django 3.2.12 on 2022-03-18 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0117_problem_short_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aigame',
            name='status',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
