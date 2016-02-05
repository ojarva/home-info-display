# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_notifications', '0002_auto_20151213_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='level',
            field=models.CharField(default=b'normal', max_length=20),
        ),
    ]
