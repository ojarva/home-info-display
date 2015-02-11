# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indoor_quality', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndoorQuality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('co2', models.IntegerField(null=True)),
                ('temperature', models.DecimalField(max_digits=6, decimal_places=2)),
            ],
            options={
                'ordering': ['-timestamp'],
                'get_latest_by': '-timestamp',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='airdatapoint',
            options={'ordering': ['-timepoint__timestamp'], 'get_latest_by': '-timepoint__timestamp'},
        ),
    ]
