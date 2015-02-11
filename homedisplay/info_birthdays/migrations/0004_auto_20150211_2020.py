# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_birthdays', '0003_auto_20150211_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='birthday',
            options={'ordering': ['name'], 'verbose_name': 'Merkkip\xe4iv\xe4', 'verbose_name_plural': 'Merkkip\xe4iv\xe4t'},
        ),
    ]
