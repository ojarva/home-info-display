# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_timers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timer',
            name='action',
            field=models.CharField(max_length=50, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timer',
            name='name',
            field=models.CharField(max_length=30),
            preserve_default=True,
        ),
    ]
