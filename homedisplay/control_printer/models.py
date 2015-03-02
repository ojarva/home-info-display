# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core import serializers
from homedisplay.utils import publish_ws
import json

__all__ = ["get_serialized_labels", "PrintLabel"]


def get_serialized_labels():
    return serializers.serialize("json", PrintLabel.objects.all())


class PrintLabel(models.Model):
    name = models.CharField(max_length=15, verbose_name="Nimi", help_text="Käyttöliittymässä näkyvä nimi")
    content = models.CharField(max_length=15, verbose_name="Sisältö", help_text="Tarralle tuleva sisältö")
    include_time = models.BooleanField(default=False, blank=True, verbose_name="Tulosta aika")
    include_date = models.BooleanField(default=False, blank=True, verbose_name="Tulosta päiväys")

    def __unicode__(self):
        return u"%s (%s), time: %s, date: %s" % (self.name, self.content, self.include_time, self.include_date)

    class Meta:
        ordering = ("name",)
        verbose_name = "Tarra"
        verbose_name_plural = "Tarrat"


def publish_items():
    publish_ws("printer-labels", json.loads(get_serialized_labels()))


@receiver(post_delete, sender=PrintLabel, dispatch_uid="printlabel_delete_signal")
def publish_printlabel_deleted(sender, instance, using, **kwargs):
    publish_items()


@receiver(post_save, sender=PrintLabel, dispatch_uid="printlabel_saved_signal")
def publish_printlabel_saved(sender, instance, created, *args, **kwargs):
    publish_items()
