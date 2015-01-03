# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0004_lightstate_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightTransformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.PositiveSmallIntegerField()),
                ('priority', models.PositiveSmallIntegerField(default=0)),
                ('to_brightness', models.PositiveSmallIntegerField(null=True)),
                ('to_nightmode', models.NullBooleanField()),
                ('to_color', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
