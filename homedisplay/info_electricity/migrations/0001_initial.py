# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Electricity',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('hour', models.PositiveSmallIntegerField()),
                ('usage', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ['date', 'hour'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='electricity',
            unique_together=set([('date', 'hour')]),
        ),
    ]
