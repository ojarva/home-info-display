# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0008_auto_20150226_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='stop',
            name='time_needed',
            field=models.IntegerField(
                default=60, help_text=b'K\xc3\xa4velyaika kotoa pys\xc3\xa4kille (sekunteina)', verbose_name=b'Aika pys\xc3\xa4kille'),
            preserve_default=False,
        ),
    ]
