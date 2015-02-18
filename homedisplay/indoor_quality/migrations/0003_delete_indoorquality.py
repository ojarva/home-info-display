# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indoor_quality', '0002_auto_20150211_1122'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IndoorQuality',
        ),
    ]
