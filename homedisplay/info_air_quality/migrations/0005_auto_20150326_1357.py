# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_air_quality', '0004_auto_20150322_1609'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='airdatapoint',
            options={'ordering': ['-timepoint__timestamp'],
                     'get_latest_by': 'timepoint__timestamp'},
        ),
        migrations.AlterModelOptions(
            name='airtimepoint',
            options={'ordering': ['-timestamp'], 'get_latest_by': 'timestamp'},
        ),
        migrations.AlterModelOptions(
            name='outsideairquality',
            options={'ordering': ['-timestamp'], 'get_latest_by': 'timestamp'},
        ),
    ]
