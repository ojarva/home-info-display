# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_air_quality', '0003_delete_indoorquality'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutsideAirQuality',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('type', models.CharField(max_length=40)),
                ('value', models.DecimalField(max_digits=7, decimal_places=2)),
            ],
            options={
                'ordering': ['-timestamp'],
                'get_latest_by': '-timestamp',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='outsideairquality',
            unique_together=set([('timestamp', 'type')]),
        ),
    ]
