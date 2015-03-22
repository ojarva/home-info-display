# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0005_weather_uv'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarineWeather',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('location', models.CharField(max_length=30)),
                ('temperature', models.DecimalField(max_digits=4, decimal_places=1)),
                ('dewpoint', models.DecimalField(max_digits=4, decimal_places=1)),
                ('humidity', models.DecimalField(max_digits=4, decimal_places=1)),
                ('cloudiness', models.PositiveSmallIntegerField()),
                ('visibility', models.IntegerField()),
                ('pressure', models.DecimalField(max_digits=5, decimal_places=1)),
                ('wind_direction', models.CharField(max_length=4)),
                ('wind_speed', models.IntegerField()),
                ('wind_gust', models.IntegerField()),
            ],
            options={
                'ordering': ('-timestamp',),
                'get_latest_by': '-timestamp',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='marineweather',
            unique_together=set([('timestamp', 'location')]),
        ),
        migrations.AlterField(
            model_name='weather',
            name='wind_direction',
            field=models.CharField(max_length=4),
            preserve_default=True,
        ),
    ]
