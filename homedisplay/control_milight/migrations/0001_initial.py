# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LightGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('rgbw_brightness', models.PositiveSmallIntegerField(null=True)),
                ('white_brightness', models.PositiveSmallIntegerField(null=True)),
                ('color', models.TextField(null=True, blank=True)),
                ('on', models.NullBooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LightTransition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('start_brightness', models.PositiveSmallIntegerField(null=True)),
                ('to_brightness', models.PositiveSmallIntegerField(null=True)),
                ('to_nightmode', models.NullBooleanField()),
                ('to_color', models.TextField(null=True, blank=True)),
                ('group', models.ForeignKey(to='control_milight.LightGroup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
