# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_weather', '0006_auto_20150322_2310'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarineDataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('location', models.CharField(max_length=50)),
                ('forecast', models.BooleanField(default=False)),
                ('air_temperature', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('water_temperature', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wave_dispersion', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wave_height', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wave_period', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wind_direction', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wind_gusts', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wind_max', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('wind_speed', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
            ],
            options={
                'ordering': ('-timestamp',),
                'get_latest_by': 'timestamp',
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='MarineWeather',
        ),
        migrations.AlterUniqueTogether(
            name='marinedatapoint',
            unique_together=set([('timestamp', 'location')]),
        ),
    ]
