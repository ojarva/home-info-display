# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0004_auto_20150222_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='weather',
            name='uv',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
