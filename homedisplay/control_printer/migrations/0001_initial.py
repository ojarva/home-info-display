# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PrintLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    help_text=b'K\xc3\xa4ytt\xc3\xb6liittym\xc3\xa4ss\xc3\xa4 n\xc3\xa4kyv\xc3\xa4 nimi', max_length=15, verbose_name=b'Nimi')),
                ('content', models.CharField(help_text=b'Tarralle tuleva sis\xc3\xa4lt\xc3\xb6',
                                             max_length=15, verbose_name=b'Sis\xc3\xa4lt\xc3\xb6')),
                ('include_time', models.BooleanField(default=False)),
                ('include_date', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Tarra',
                'verbose_name_plural': 'Tarrat',
            },
            bases=(models.Model,),
        ),
    ]
