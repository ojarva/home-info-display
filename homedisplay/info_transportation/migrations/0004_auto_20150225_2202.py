# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0003_line_show_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(
                2015, 2, 25, 20, 2, 14, 104155, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stop',
            name='stop_number',
            field=models.CharField(unique=True, max_length=20),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='data',
            unique_together=set([('line', 'time')]),
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together=set([('stop', 'line_number')]),
        ),
    ]
