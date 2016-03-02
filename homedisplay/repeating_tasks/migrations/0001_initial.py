# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('repeat_every_n_seconds', models.IntegerField()),
                ('last_completed_at', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('completed_at', models.DateTimeField(null=True)),
                ('task', models.ForeignKey(to='repeating_tasks.Task')),
            ],
            options={
                'get_latest_by': 'completed_at',
            },
            bases=(models.Model,),
        ),
    ]
