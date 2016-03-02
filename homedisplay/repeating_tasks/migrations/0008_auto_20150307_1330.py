# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0007_auto_20150224_1046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskhistory',
            options={'ordering': ('completed_at',),
                     'get_latest_by': 'completed_at'},
        ),
        migrations.AlterField(
            model_name='taskhistory',
            name='task',
            field=models.ForeignKey(
                related_name='tasks', to='repeating_tasks.Task'),
            preserve_default=True,
        ),
    ]
