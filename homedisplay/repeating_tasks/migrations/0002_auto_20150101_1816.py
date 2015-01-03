# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='last_completed_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
