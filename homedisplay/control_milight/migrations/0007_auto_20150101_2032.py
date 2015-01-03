# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0006_lighttransformation_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightTransition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.PositiveSmallIntegerField()),
                ('description', models.TextField(null=True, blank=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('start_brightness', models.PositiveSmallIntegerField(null=True)),
                ('to_brightness', models.PositiveSmallIntegerField(null=True)),
                ('to_nightmode', models.NullBooleanField()),
                ('to_color', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='LightTransformation',
        ),
    ]
