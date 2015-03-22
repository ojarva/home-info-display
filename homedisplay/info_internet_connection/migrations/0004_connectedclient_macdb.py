# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_internet_connection', '0003_internet_update_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectedClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mac', models.CharField(unique=True, max_length=17)),
                ('rssi', models.IntegerField(null=True, blank=True)),
                ('bandwidth_in', models.IntegerField(null=True, blank=True)),
                ('bandwidth_out', models.IntegerField(null=True, blank=True)),
                ('tx', models.BigIntegerField(null=True, blank=True)),
                ('rx', models.BigIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MacDb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mac', models.CharField(unique=True, max_length=17)),
                ('hostname', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
