# Generated by Django 3.1.6 on 2021-02-08 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comuna',
            fields=[
                ('comuna_id', models.IntegerField(primary_key=True, serialize=False)),
                ('comuna_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('region_id', models.IntegerField(primary_key=True, serialize=False)),
                ('region_number', models.CharField(max_length=4)),
                ('region_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('hospital_id', models.IntegerField(primary_key=True, serialize=False)),
                ('hospital_name', models.CharField(max_length=255)),
                ('hospital_image_path', models.CharField(max_length=255)),
                ('comuna_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.comuna')),
            ],
        ),
        migrations.AddField(
            model_name='comuna',
            name='region_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.region'),
        ),
    ]