# Generated by Django 3.1.6 on 2021-02-08 01:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_medicslastupdate'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MedicsLastUpdate',
            new_name='HospitalLastUpdate',
        ),
    ]
