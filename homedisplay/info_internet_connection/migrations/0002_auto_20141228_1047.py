# -*- coding: utf-8 -*-
# pylint:disable=invalid-name,too-few-public-methods,no-name-in-module,bad-continuation
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_internet_connection', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='internet',
            options={'get_latest_by': 'timestamp'},
        ),
        migrations.AlterField(
            model_name='internet',
            name='connect_status',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(
                b'no_connect', b'no_connect'), (b'connecting', b'connecting_now'), (b'connected', b'connected')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='internet',
            name='mode',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(
                b'off', b'off'), (b'2g', b'2g'), (b'3g', b'3g'), (b'4g', b'4g'), (b'sim_disabled', b'sim_disabled')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='internet',
            name='sim',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(
                b'no_sim', b'No SIM installed'), (b'normal', b'normal'), (b'pin_locked', b'requires PIN'), (b'error', b'error')]),
            preserve_default=True,
        ),
    ]
