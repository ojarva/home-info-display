# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_birthdays', '0002_auto_20150205_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='birthday',
            name='birthday',
            field=models.DateField(verbose_name=b'Merkkip\xc3\xa4iv\xc3\xa4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='birthday',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'Nimi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='birthday',
            name='nickname',
            field=models.CharField(help_text=b'Jos t\xc3\xa4ytetty, n\xc3\xa4ytet\xc3\xa4\xc3\xa4n nimen sijaan', max_length=100, null=True, verbose_name=b'Lempinimi', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='birthday',
            name='valid_year',
            field=models.NullBooleanField(default=True, help_text=b'Onko vuosi oikein? Jos ei, ik\xc3\xa4\xc3\xa4 ei n\xc3\xa4ytet\xc3\xa4.', verbose_name=b'Vuosi oikein'),
            preserve_default=True,
        ),
    ]
