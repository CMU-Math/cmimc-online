# Generated by Django 3.2.12 on 2022-02-24 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0113_alter_exam_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='real_end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
