# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from homedisplay.utils import publish_ws
import datetime
import json

def get_birthdays(selected_date):
    if selected_date == "all":
        items = Birthday.objects.all()
    else:
        date = datetime.date.today()
        if selected_date == "tomorrow":
            date = date + datetime.timedelta(days=1)

        items = Birthday.objects.filter(birthday__month=date.month, birthday__day=date.day)
    return json.loads(serializers.serialize("json", items))


class Birthday(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nimi")
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name="Lempinimi", help_text="Jos täytetty, näytetään nimen sijaan")
    birthday = models.DateField(verbose_name="Merkkipäivä")
    valid_year = models.NullBooleanField(default=True, verbose_name="Vuosi oikein", help_text="Onko vuosi oikein? Jos ei, ikää ei näytetä.")

    @property
    def age(self):
        diff = now() - self.birthday
        return int(diff.days / 365.2425)

    def __unicode__(self):
        return u"%s (%s) %s (valid_year=%s)" % (self.name, self.nickname, self.birthday, self.valid_year)

    class Meta:
        ordering = ["name"]
        verbose_name = "Merkkipäivä"
        verbose_name_plural = "Merkkipäivät"

def publish_changes():
    for k in ("today", "tomorrow", "all"):
        publish_ws("birthdays_%s" % k, get_birthdays(k))

@receiver(post_delete, sender=Birthday, dispatch_uid='birthday_delete_signal')
def publish_birthday_deleted(sender, instance, using, **kwargs):
    publish_changes();

@receiver(post_save, sender=Birthday, dispatch_uid="birthday_saved_signal")
def publish_birthday_saved(sender, instance, *args, **kwargs):
    publish_changes()
