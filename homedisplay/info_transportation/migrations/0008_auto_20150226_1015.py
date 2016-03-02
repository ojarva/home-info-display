# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_transportation', '0007_auto_20150226_0932'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='line',
            options={'verbose_name': 'Linja', 'verbose_name_plural': 'Linjat'},
        ),
        migrations.AlterModelOptions(
            name='stop',
            options={'verbose_name': 'Pys\xe4kki',
                     'verbose_name_plural': 'Pys\xe4kit'},
        ),
        migrations.AddField(
            model_name='line',
            name='destination',
            field=models.CharField(default=' ', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='line',
            name='raw',
            field=models.CharField(
                default=' ', max_length=50, verbose_name=b'Sis\xc3\xa4inen numero'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='line',
            name='line_number',
            field=models.CharField(max_length=20, verbose_name=b'Numero'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='line',
            name='line_number_raw',
            field=models.CharField(max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='line',
            name='show_line',
            field=models.BooleanField(
                default=False, verbose_name=b'N\xc3\xa4yt\xc3\xa4 l\xc3\xa4hd\xc3\xb6t'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stop',
            name='description',
            field=models.CharField(max_length=50, verbose_name=b'Kuvaus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stop',
            name='stop_number',
            field=models.CharField(
                unique=True, max_length=20, verbose_name=b'Numero'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together=set([('stop', 'raw')]),
        ),
    ]
