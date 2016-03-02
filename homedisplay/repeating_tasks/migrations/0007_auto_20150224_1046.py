# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0006_auto_20150211_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='trigger_every_day_of_month',
            field=models.SmallIntegerField(
                null=True, verbose_name=b'Toista tiettyn\xc3\xa4 p\xc3\xa4iv\xc3\xa4n\xc3\xa4 kuukaudesta', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='trigger_every_weekday',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name=b'Toista tiettyn\xc3\xa4 viikonp\xc3\xa4iv\xc3\xa4n\xc3\xa4', choices=[(
                b'ma', b'maanantai'), (b'ti', b'tiistai'), (b'ke', b'keskiviikko'), (b'to', b'torstai'), (b'pe', b'perjantai'), (b'la', b'lauantai'), (b'su', b'sunnuntai')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='repeat_every_n_seconds',
            field=models.IntegerField(help_text=b'Toistov\xc3\xa4li sekunteina',
                                      null=True, verbose_name=b'Toista joka n:s sekunti', blank=True),
            preserve_default=True,
        ),
    ]
