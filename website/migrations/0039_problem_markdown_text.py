# Generated by Django 3.1.4 on 2020-12-12 22:34

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0038_auto_20201210_2346'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='markdown_text',
            field=markdownx.models.MarkdownxField(default=''),
            preserve_default=False,
        ),
    ]