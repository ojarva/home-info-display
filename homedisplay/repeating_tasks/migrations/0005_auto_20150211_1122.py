# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repeating_tasks', '0004_task_snooze'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='last_completed_at',
            field=models.DateTimeField(help_text=b'Edellinen kerta kun teht\xc3\xa4v\xc3\xa4 on tehty',
                                       null=True, verbose_name=b'Edellinen valmistuminen', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='optional',
            field=models.NullBooleanField(
                default=False, help_text=b'Kyll\xc3\xa4, jos tarkoituksena on tarkistaa, eik\xc3\xa4 tehd\xc3\xa4 joka kerta.', verbose_name=b'Optionaalinen'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='repeat_every_n_seconds',
            field=models.IntegerField(
                help_text=b'Toistov\xc3\xa4li sekunteina', verbose_name=b'Toista joka n:s sekunti'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='snooze',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.TextField(verbose_name=b'Otsikko'),
            preserve_default=True,
        ),
    ]
