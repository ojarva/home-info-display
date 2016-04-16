# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core import serializers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from homedisplay.utils import publish_ws
import datetime
import json


class NfcTag(models.Model):
    tag_id = models.CharField(max_length=50, verbose_name="ID")
    name = models.CharField(max_length=100, verbose_name="Nimi")
    boil_water = models.IntegerField(null=True, blank=True, verbose_name="Keitä vesi (C)")
    created_at = models.DateTimeField(auto_now_add=True)
    first_used_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)


class NfcTagAction(models.Model):
    tag = models.ForeignKey("NfcTag")
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)


def publish_changes():
    items = NfcTag.objects.all()
    return json.loads(serializers.serialize("json", items))


@receiver(post_delete, sender=NfcTag, dispatch_uid='nfctag_delete_signal')
def publish_nfctag_deleted(sender, instance, using, **kwargs):
    publish_changes()


@receiver(post_save, sender=NfcTag, dispatch_uid="nfctag_save_signal")
def publish_nfctag_saved(sender, instance, *args, **kwargs):
    publish_changes()
