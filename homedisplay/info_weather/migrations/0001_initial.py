# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('hour', models.PositiveSmallIntegerField()),
                ('icon', models.TextField()),
                ('ppcp', models.PositiveSmallIntegerField()),
                ('dewpoint', models.IntegerField()),
                ('feels_like', models.IntegerField()),
                ('humidity', models.PositiveSmallIntegerField()),
                ('temperature', models.IntegerField()),
                ('description', models.TextField()),
                ('wind_direction', models.TextField()),
                ('wind_gust', models.TextField()),
                ('wind_speed', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
