# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0003_auto_20141228_0104'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightstate',
            name='on',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
