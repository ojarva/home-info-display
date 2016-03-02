# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_printer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printlabel',
            name='include_date',
            field=models.BooleanField(
                default=False, verbose_name=b'Tulosta p\xc3\xa4iv\xc3\xa4ys'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='printlabel',
            name='include_time',
            field=models.BooleanField(
                default=False, verbose_name=b'Tulosta aika'),
            preserve_default=True,
        ),
    ]
