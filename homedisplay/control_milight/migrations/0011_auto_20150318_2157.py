# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control_milight', '0010_lightautomation_turn_display_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightgroup',
            name='on_automatically',
            field=models.BooleanField(default=False, help_text=b'Onko ryhm\xc3\xa4 p\xc3\xa4\xc3\xa4ll\xc3\xa4 automaattisesti vai manuaalisesti', verbose_name=b'P\xc3\xa4\xc3\xa4ll\xc3\xa4 automaattisesti'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lightgroup',
            name='on_until',
            field=models.DateTimeField(help_text=b'Aika, johon asti valo pidet\xc3\xa4\xc3\xa4n p\xc3\xa4\xc3\xa4ll\xc3\xa4', null=True, verbose_name=b'Automaattinen sammutusaika', blank=True),
            preserve_default=True,
        ),
    ]
