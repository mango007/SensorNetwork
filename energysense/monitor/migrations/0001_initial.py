# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Energymonitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nodeid', models.IntegerField()),
                ('time', models.DateTimeField()),
                ('voltage', models.FloatField()),
                ('cumcurr', models.FloatField()),
                ('data', models.CharField(max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('sensor_id', models.IntegerField(serialize=False, primary_key=True)),
                ('last_connected_time', models.DateTimeField()),
                ('initial_energy', models.FloatField()),
                ('remaining_energy', models.FloatField()),
                ('is_base_station', models.IntegerField()),
                ('last_voltage', models.FloatField()),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sensorID1', models.IntegerField()),
                ('sensorID2', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User_Sensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('sensor_id', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
