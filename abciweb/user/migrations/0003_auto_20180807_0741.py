# Generated by Django 2.0.7 on 2018-08-07 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20180807_0739'),
    ]

    operations = [
        migrations.RenameField(
            model_name='abciuser',
            old_name='prevkey_file',
            new_name='prvkey_file',
        ),
    ]
