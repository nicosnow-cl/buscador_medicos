# Generated by Django 3.1.6 on 2021-02-08 01:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_medic'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicsLastUpdate',
            fields=[
                ('last_update_id', models.IntegerField(primary_key=True, serialize=False)),
                ('last_update_datetime', models.DateTimeField(auto_now=True)),
                ('hospital_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.hospital')),
            ],
        ),
    ]