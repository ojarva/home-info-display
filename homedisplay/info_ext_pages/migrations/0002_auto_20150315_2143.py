# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_ext_pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extpage',
            options={'ordering': ('timestamp',), 'get_latest_by': 'timestamp',
                     'verbose_name': 'Osoite', 'verbose_name_plural': 'Osoitteet'},
        ),
    ]
