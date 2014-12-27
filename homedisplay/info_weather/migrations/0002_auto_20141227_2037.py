# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='weather',
            unique_together=set([('date', 'hour')]),
        ),
    ]
