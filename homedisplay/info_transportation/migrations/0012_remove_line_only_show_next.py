# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0011_line_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='line',
            name='only_show_next',
        ),
    ]
