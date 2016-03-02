# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0012_remove_line_only_show_next'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineShow',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=30)),
                ('show_start', models.TimeField(help_text=b'N\xc3\xa4yt\xc3\xa4 l\xc3\xa4hd\xc3\xb6t t\xc3\xa4m\xc3\xa4n ajan j\xc3\xa4lkeen',
                                                null=True, verbose_name=b'Aloitusaika', blank=True)),
                ('show_end', models.TimeField(help_text=b'N\xc3\xa4yt\xc3\xa4 l\xc3\xa4hd\xc3\xb6t ennen t\xc3\xa4t\xc3\xa4 aikaa',
                                              null=True, verbose_name=b'Lopetusaika', blank=True)),
                ('show_days', models.CharField(default=b'1111111', help_text=b'ma-su, 1=p\xc3\xa4\xc3\xa4ll\xc3\xa4, 0=pois p\xc3\xa4\xc3\xa4lt\xc3\xa4',
                                               max_length=7, verbose_name=b'N\xc3\xa4yt\xc3\xa4 tiettyin\xc3\xa4 p\xc3\xa4ivin\xc3\xa4')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='line',
            name='show_times',
            field=models.ManyToManyField(to='info_transportation.LineShow'),
            preserve_default=True,
        ),
    ]
