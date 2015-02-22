# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0006_auto_20150217_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lighttransition',
            name='group',
        ),
        migrations.DeleteModel(
            name='LightTransition',
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='active_days',
            field=models.CharField(default=b'0000000', max_length=7),
            preserve_default=True,
        ),
    ]
