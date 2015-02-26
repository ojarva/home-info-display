# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0002_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='show_line',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
