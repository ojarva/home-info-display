# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_birthdays', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='birthday',
            name='nickname',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='birthday',
            name='name',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]
