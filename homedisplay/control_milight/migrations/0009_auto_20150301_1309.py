# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0008_auto_20150301_1257'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lightautomation',
            options={'ordering': ('action',), 'verbose_name': 'Valo-ohjelma',
                     'verbose_name_plural': 'Valo-ohjelmat'},
        ),
        migrations.AlterModelOptions(
            name='lightgroup',
            options={'ordering': ('group_id',), 'verbose_name': 'Valoryhm\xe4',
                     'verbose_name_plural': 'Valoryhm\xe4t'},
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='action',
            field=models.CharField(
                unique=True, max_length=30, verbose_name=b'Sis\xc3\xa4inen nimi toiminnolle'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightgroup',
            name='color',
            field=models.TextField(
                null=True, verbose_name=b'V\xc3\xa4ri', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightgroup',
            name='description',
            field=models.CharField(
                max_length=20, null=True, verbose_name=b'Kuvaus', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightgroup',
            name='group_id',
            field=models.PositiveSmallIntegerField(
                unique=True, verbose_name=b'Numero'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightgroup',
            name='on',
            field=models.NullBooleanField(
                verbose_name=b'P\xc3\xa4\xc3\xa4ll\xc3\xa4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightgroup',
            name='rgbw_brightness',
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name=b'V\xc3\xa4rillisen kirkkaus'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightgroup',
            name='white_brightness',
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name=b'Valkoisen kirkkaus'),
            preserve_default=True,
        ),
    ]
