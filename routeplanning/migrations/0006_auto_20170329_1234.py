# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-29 12:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0005_flightassignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.IntegerField(default=0)),
                ('departure_datetime', models.DateTimeField()),
                ('status', models.IntegerField(choices=[(1, 'Flight'), (2, 'Maintenance')], default=1)),
                ('flight', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='routeplanning.Flight')),
                ('tail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='routeplanning.Tail')),
            ],
        ),
        migrations.RemoveField(
            model_name='flightassignment',
            name='flight',
        ),
        migrations.RemoveField(
            model_name='flightassignment',
            name='tail',
        ),
        migrations.DeleteModel(
            name='FlightAssignment',
        ),
    ]
