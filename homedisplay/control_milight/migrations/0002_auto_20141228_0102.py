# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lightstate',
            name='id',
        ),
        migrations.AlterField(
            model_name='lightstate',
            name='group',
            field=models.PositiveSmallIntegerField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
