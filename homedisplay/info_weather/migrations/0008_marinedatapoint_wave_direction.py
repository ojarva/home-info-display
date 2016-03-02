# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0007_auto_20150326_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='marinedatapoint',
            name='wave_direction',
            field=models.DecimalField(
                null=True, max_digits=4, decimal_places=1, blank=True),
            preserve_default=True,
        ),
    ]
