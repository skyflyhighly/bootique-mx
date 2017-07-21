# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-17 13:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('target', models.IntegerField(choices=[(1, 'Aircraft'), (2, 'Airframe'), (3, 'Engine'), (4, 'Propeller')], default=1)),
                ('interval', models.IntegerField(default=0)),
                ('interval_unit', models.CharField(default='hours', max_length=10)),
            ],
            options={
                'db_table': 'inspection',
            },
        ),
        migrations.CreateModel(
            name='InspectionProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'inspection_program',
            },
        ),
        migrations.AddField(
            model_name='inspection',
            name='inspection_program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection.InspectionProgram'),
        ),
    ]