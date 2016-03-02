# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0005_auto_20150211_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'verbose_name': 'Toistuva teht\xe4v\xe4',
                     'verbose_name_plural': 'Toistuvat teht\xe4v\xe4t'},
        ),
    ]
