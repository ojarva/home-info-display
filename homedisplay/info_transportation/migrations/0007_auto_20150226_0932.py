# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0006_line_line_destination'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='line',
            name='line_destination',
        ),
        migrations.AlterField(
            model_name='line',
            name='line_number_raw',
            field=models.CharField(max_length=50),
            preserve_default=True,
        ),
    ]
