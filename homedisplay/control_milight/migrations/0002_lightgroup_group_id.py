# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightgroup',
            name='group_id',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]
