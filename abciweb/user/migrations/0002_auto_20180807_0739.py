# Generated by Django 2.0.7 on 2018-08-07 07:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='ABCIUser',
        ),
        migrations.RenameModel(
            old_name='Template',
            new_name='DataTemplate',
        ),
    ]