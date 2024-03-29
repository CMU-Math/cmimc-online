# Generated by Django 3.2.12 on 2022-03-17 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0106_auto_20211223_2238'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIVisualizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('visualizer', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='alias',
            field=models.CharField(blank=True, help_text='preferred name', max_length=100, verbose_name='alias'),
        ),
        migrations.AlterField(
            model_name='user',
            name='full_name',
            field=models.CharField(blank=True, help_text='full name', max_length=300, verbose_name='full name'),
        ),
    ]
