# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 18:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0018_auto_20160205_2022'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='data',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='data',
            name='line',
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='line',
            name='show_times',
        ),
        migrations.RemoveField(
            model_name='line',
            name='stop',
        ),
        migrations.DeleteModel(
            name='Data',
        ),
        migrations.DeleteModel(
            name='Line',
        ),
        migrations.DeleteModel(
            name='LineShow',
        ),
        migrations.DeleteModel(
            name='Stop',
        ),
    ]
