# Generated by Django 3.2.7 on 2021-09-24 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20210924_2045'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscriber',
            old_name='subscriber',
            new_name='user',
        ),
    ]
