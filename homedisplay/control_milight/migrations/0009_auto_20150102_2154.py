# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0008_auto_20150102_2143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lightgroup',
            name='group',
        ),
        migrations.AddField(
            model_name='lightgroup',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, default=1, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
