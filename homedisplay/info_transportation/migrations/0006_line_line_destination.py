# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0005_auto_20150225_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='line_destination',
            field=models.CharField(default='1', max_length=50),
            preserve_default=False,
        ),
    ]
