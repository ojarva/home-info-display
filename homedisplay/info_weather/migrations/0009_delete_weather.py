# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0008_marinedatapoint_wave_direction'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Weather',
        ),
    ]
