# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-11 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routeplanning', '0013_auto_20170403_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.IntegerField(choices=[(1, 'Flight'), (2, 'Maintenance'), (3, 'Unscheduled Flight')], default=1),
        ),
    ]
