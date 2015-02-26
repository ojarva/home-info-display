# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0010_line_only_show_next'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='icon',
            field=models.CharField(default=b'bus', max_length=10, verbose_name=b'Ikoni', choices=[(b'bus', b'bus'), (b'train', b'train')]),
            preserve_default=True,
        ),
    ]
