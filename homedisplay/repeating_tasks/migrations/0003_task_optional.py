# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0002_auto_20150101_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='optional',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]
