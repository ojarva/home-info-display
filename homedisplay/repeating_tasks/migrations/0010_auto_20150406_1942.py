# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0009_auto_20150307_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=100, verbose_name=b'Otsikko'),
            preserve_default=True,
        ),
    ]
