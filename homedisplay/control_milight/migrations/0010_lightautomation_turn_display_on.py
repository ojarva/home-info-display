# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0009_auto_20150301_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightautomation',
            name='turn_display_on',
            field=models.BooleanField(default=False, help_text=b'K\xc3\xa4ynnist\xc3\xa4 n\xc3\xa4ytt\xc3\xb6 ohjelman alussa', verbose_name=b'K\xc3\xa4ynnist\xc3\xa4 n\xc3\xa4ytt\xc3\xb6'),
            preserve_default=True,
        ),
    ]
