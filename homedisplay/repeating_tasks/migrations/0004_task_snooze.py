# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0003_task_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='snooze',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
