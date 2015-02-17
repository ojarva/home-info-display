# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0005_auto_20150217_2050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lightautomation',
            name='active_weekdays',
        ),
        migrations.RemoveField(
            model_name='lightautomation',
            name='active_weekend',
        ),
        migrations.AddField(
            model_name='lightautomation',
            name='active_days',
            field=models.CharField(default=b'0000001', max_length=7),
            preserve_default=True,
        ),
    ]
