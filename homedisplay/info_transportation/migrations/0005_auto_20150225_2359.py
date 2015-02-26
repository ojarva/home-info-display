# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0004_auto_20150225_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='line_number_raw',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together=set([('stop', 'line_number_raw')]),
        ),
    ]
