# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ('-timestamp',),
                     'get_latest_by': 'timestamp'},
        ),
        migrations.AddField(
            model_name='notification',
            name='elapsed_since',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='from_now_timestamp',
            field=models.DateTimeField(null=True),
        ),
    ]
