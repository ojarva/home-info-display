# -*- coding: utf-8 -*-
# pylint:disable=invalid-name,too-few-public-methods,no-name-in-module,bad-continuation
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_internet_connection', '0002_auto_20141228_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='internet',
            name='update_timestamp',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
