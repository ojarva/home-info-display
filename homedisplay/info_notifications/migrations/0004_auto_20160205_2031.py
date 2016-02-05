# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_notifications', '0003_notification_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='item_type',
            field=models.CharField(max_length=50),
        ),
    ]
