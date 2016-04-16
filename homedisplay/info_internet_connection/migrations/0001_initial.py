# -*- coding: utf-8 -*-
# pylint:disable=invalid-name,too-few-public-methods,no-name-in-module,bad-continuation,duplicate-code
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Internet',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('wifi', models.NullBooleanField()),
                ('signal', models.PositiveSmallIntegerField(null=True)),
                ('mode', models.CharField(blank=True, max_length=3, null=True, choices=[
                 (b'off', b'off'), (b'2g', b'2g'), (b'3g', b'3g'), (b'4g', b'4g'), (b'sim', b'sim_disabled')])),
                ('sim', models.CharField(blank=True, max_length=3, null=True, choices=[
                 (b'NS', b'no_sim'), (b'N', b'normal'), (b'L', b'locked'), (b'E', b'error')])),
                ('connect_status', models.CharField(blank=True, max_length=3, null=True, choices=[
                 (b'NC', b'no_connect'), (b'CN', b'connecting_now'), (b'C', b'connected')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
