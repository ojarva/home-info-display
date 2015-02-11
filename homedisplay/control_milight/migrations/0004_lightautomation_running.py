# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0003_lightautomation'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightautomation',
            name='running',
            field=models.NullBooleanField(default=True),
            preserve_default=True,
        ),
    ]
