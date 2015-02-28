# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_timers', '0003_auto_20150228_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='timer',
            name='auto_remove',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timer',
            name='no_refresh',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
