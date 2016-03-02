# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0017_auto_20150322_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='line',
            name='show_times',
            field=models.ManyToManyField(
                to='info_transportation.LineShow', blank=True),
        ),
    ]
