# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0008_auto_20150307_1330'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskhistory',
            options={'ordering': ('-completed_at',),
                     'get_latest_by': 'completed_at'},
        ),
        migrations.AddField(
            model_name='task',
            name='show_immediately',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
