# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-30 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection', '0011_auto_20170526_0617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspectioncomponent',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='inspectioncomponent',
            name='pn',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='inspectioncomponent',
            name='sn',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='inspectionprogram',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='inspectiontask',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
