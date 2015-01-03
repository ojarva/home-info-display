# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0007_auto_20150101_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightGroup',
            fields=[
                ('group', models.PositiveSmallIntegerField(serialize=False, primary_key=True)),
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
        migrations.DeleteModel(
            name='LightState',
        ),
        migrations.AlterField(
            model_name='lighttransition',
            name='group',
            field=models.ForeignKey(to='control_milight.LightGroup'),
            preserve_default=True,
        ),
    ]
