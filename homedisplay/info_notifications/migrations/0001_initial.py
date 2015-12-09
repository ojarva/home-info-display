# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('item_type', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('can_dismiss', models.NullBooleanField()),
            ],
            options={
                'ordering': ('timestamp',),
                'get_latest_by': 'timestamp',
            },
        ),
    ]
