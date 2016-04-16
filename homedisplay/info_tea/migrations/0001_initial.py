# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-29 13:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NfcTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_id', models.CharField(max_length=50, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nimi')),
                ('boil_water', models.IntegerField(blank=True, null=True, verbose_name='Keit\xe4 vesi (C)')),
                ('first_used_at', models.DateTimeField(blank=True, null=True)),
                ('last_used_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NfcTagAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=100)),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info_tea.NfcTag')),
            ],
        ),
    ]