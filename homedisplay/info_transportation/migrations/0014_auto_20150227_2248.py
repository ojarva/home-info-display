# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0013_auto_20150227_2105'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lineshow',
            options={'verbose_name': 'N\xe4yt\xf6n aikataulu', 'verbose_name_plural': 'N\xe4yt\xf6n aikataulut'},
        ),
        migrations.AlterField(
            model_name='line',
            name='show_times',
            field=models.ManyToManyField(to='info_transportation.LineShow', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lineshow',
            name='description',
            field=models.CharField(max_length=30, verbose_name=b'Nimi'),
            preserve_default=True,
        ),
    ]
