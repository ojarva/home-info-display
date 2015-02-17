# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0004_lightautomation_running'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightautomation',
            name='active_weekdays',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lightautomation',
            name='active_weekend',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
