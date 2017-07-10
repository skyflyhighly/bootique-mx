# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-24 12:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection', '0004_auto_20170524_0455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspectiontask',
            name='inspection_program',
        ),
        migrations.AlterField(
            model_name='inspectiontask',
            name='target',
            field=models.IntegerField(choices=[(1, 'Aircraft'), (2, 'Airframe'), (3, 'Propeller'), (4, 'Engine')], default=1),
        ),
    ]
