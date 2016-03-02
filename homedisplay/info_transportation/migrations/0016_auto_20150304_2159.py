# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0015_line_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='line',
            name='type',
            field=models.CharField(default=b'bus', help_text=b'Liikennev\xc3\xa4linetyyppi', max_length=10, verbose_name=b'Tyyppi', choices=[
                                   (b'bus', b'bus'), (b'tram', b'tram'), (b'train', b'train'), (b'metro', b'metro')]),
            preserve_default=True,
        ),
    ]
