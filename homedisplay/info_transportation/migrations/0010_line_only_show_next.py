# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0009_stop_time_needed'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='only_show_next',
            field=models.BooleanField(
                default=False, verbose_name=b'N\xc3\xa4yt\xc3\xa4 vain seuraava'),
            preserve_default=True,
        ),
    ]
