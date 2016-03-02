# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_timers', '0002_auto_20150211_1122'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Ajastimen teksti',
                'verbose_name_plural': 'Ajastimien tekstit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimedCustomLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('duration', models.IntegerField()),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Ajastin valmiilla ajalla',
                'verbose_name_plural': 'Ajastimet valmiilla ajoilla',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='timer',
            options={'ordering': (
                'name', 'start_time'), 'verbose_name': 'Ajastin', 'verbose_name_plural': 'Ajastimet'},
        ),
    ]
