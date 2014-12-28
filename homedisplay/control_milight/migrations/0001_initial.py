# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LightState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.PositiveSmallIntegerField()),
                ('rgbw_brightness', models.PositiveSmallIntegerField()),
                ('white_brightness', models.PositiveSmallIntegerField()),
                ('color', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
