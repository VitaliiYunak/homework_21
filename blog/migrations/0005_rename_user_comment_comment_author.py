# Generated by Django 5.1.3 on 2024-12-01 22:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_comment_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='user',
            new_name='comment_author',
        ),
    ]
