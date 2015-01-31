# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0002_auto_20141227_2037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weather',
            options={'ordering': ['date', 'hour']},
        ),
    ]
