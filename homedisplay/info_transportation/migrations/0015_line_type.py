# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0014_auto_20150227_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='type',
            field=models.CharField(default=b'bus', help_text=b'Liikennev\xc3\xa4linetyyppi', max_length=10, verbose_name=b'Tyyppi', choices=[(b'bus', b'bus'), (b'tram', b'tram'), (b'train', b'train')]),
            preserve_default=True,
        ),
    ]
