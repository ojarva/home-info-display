# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_timers', '0004_auto_20150228_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='timer',
            name='alarm_0s',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timer',
            name='alarm_300s',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timer',
            name='alarm_30s',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timer',
            name='alarm_600s',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timer',
            name='alarm_60s',
            field=models.BooleanField(default=False),
        ),
    ]
