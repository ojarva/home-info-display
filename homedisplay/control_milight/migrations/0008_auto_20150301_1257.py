# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0007_auto_20150222_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightautomation',
            name='action_if_off',
            field=models.BooleanField(default=True, help_text=b'Suorita ohjelma my\xc3\xb6s sammutetuille valoille', verbose_name=b'Suorita sammutetuille'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lightautomation',
            name='no_brighten',
            field=models.BooleanField(default=False, help_text=b'Jos raksitettu, valojen kirkkautta ei koskaan lis\xc3\xa4t\xc3\xa4', verbose_name=b'\xc3\x84l\xc3\xa4 lis\xc3\xa4\xc3\xa4 valojen kirkkautta'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lightautomation',
            name='no_dimming',
            field=models.BooleanField(default=False, help_text=b'Jos raksitettu, valojen kirkkautta ei koskaan v\xc3\xa4hennet\xc3\xa4', verbose_name=b'\xc3\x84l\xc3\xa4 v\xc3\xa4henn\xc3\xa4 valojen kirkkautta'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lightautomation',
            name='set_white',
            field=models.BooleanField(default=False, help_text=b'Vaihda ohjelman aikana v\xc3\xa4ri valkoiseksi', verbose_name=b'Vaihda v\xc3\xa4ri valkoiseksi'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='action',
            field=models.CharField(max_length=30, verbose_name=b'Sis\xc3\xa4inen nimi toiminnolle'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='active_days',
            field=models.CharField(default=b'0000000', help_text=b'ma-su, 0=pois, 1=p\xc3\xa4\xc3\xa4ll\xc3\xa4', max_length=7, verbose_name=b'P\xc3\xa4iv\xc3\xa4t'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='duration',
            field=models.IntegerField(verbose_name=b'Kestoaika sekunteina'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='running',
            field=models.NullBooleanField(default=True, verbose_name=b'P\xc3\xa4\xc3\xa4ll\xc3\xa4'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='lightautomation',
            name='start_time',
            field=models.TimeField(verbose_name=b'Aloitusaika'),
            preserve_default=True,
        ),
    ]
