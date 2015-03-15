# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExtPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('url', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ('timestamp',),
                'verbose_name': 'Osoite',
                'verbose_name_plural': 'Osoitteet',
            },
            bases=(models.Model,),
        ),
    ]
