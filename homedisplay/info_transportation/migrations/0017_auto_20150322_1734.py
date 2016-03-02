# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0016_auto_20150304_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='line',
            name='icon',
            field=models.CharField(default=b'bus', max_length=10, verbose_name=b'Ikoni', choices=[(
                b'bus', b'bus'), (b'train', b'train'), (b'subway', b'subway'), (b'ship', b'ship'), (b'plane', b'plane')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='line',
            name='type',
            field=models.CharField(default=b'bus', help_text=b'Liikennev\xc3\xa4linetyyppi', max_length=10, verbose_name=b'Tyyppi', choices=[
                                   (b'bus', b'bus'), (b'tram', b'tram'), (b'train', b'train'), (b'metro', b'metro'), (b'ship', b'ship'), (b'plane', b'plane')]),
            preserve_default=True,
        ),
    ]
