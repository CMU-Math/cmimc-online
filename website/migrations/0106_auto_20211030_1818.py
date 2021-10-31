# Generated by Django 3.1.7 on 2021-10-30 22:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0105_auto_20211030_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waiver',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waiver', to=settings.AUTH_USER_MODEL),
        ),
    ]
