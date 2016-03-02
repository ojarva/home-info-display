# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0011_auto_20150318_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightautomation',
            name='turn_display_off',
            field=models.BooleanField(
                default=False, help_text=b'Sammuta n\xc3\xa4ytt\xc3\xb6 ohjelman lopussa', verbose_name=b'Sammuta n\xc3\xa4ytt\xc3\xb6'),
        ),
    ]
