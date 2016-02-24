# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_timers', '0005_auto_20160213_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timer',
            name='no_refresh',
        ),
        migrations.AddField(
            model_name='timer',
            name='alarm_until_dismissed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timer',
            name='no_bell',
            field=models.BooleanField(default=False),
        ),
    ]
