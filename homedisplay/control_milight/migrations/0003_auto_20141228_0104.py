# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0002_auto_20141228_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lightstate',
            name='color',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightstate',
            name='rgbw_brightness',
            field=models.PositiveSmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightstate',
            name='white_brightness',
            field=models.PositiveSmallIntegerField(null=True),
            preserve_default=True,
        ),
    ]
