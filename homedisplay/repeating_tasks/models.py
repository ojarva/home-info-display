# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from homedisplay.utils import publish_ws
import datetime
import json
import logging

logger = logging.getLogger(__name__)


def get_repeating_data(date, serialized=False):
    todo_tasks = []
    tasks = Task.objects.all()
    tasks = sorted(tasks, key=lambda t: t.overdue_by())
    tasks.reverse()
    if date == "today":
        day_starts = now().replace(hour=0, minute=0, second=0)
        day_ends = now().replace(hour=23, minute=59, second=59)
    elif date == "tomorrow":
        day_starts = now().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
        day_ends = now().replace(hour=23, minute=59, second=59) + datetime.timedelta(days=1)
    else:
        day_starts = day_ends = None
    for task in tasks:
        exp_at = task.expires_at()
        if day_starts and day_ends:
            if day_starts < exp_at and day_ends > exp_at:
                todo_tasks.append(task)
        elif date == "all":
            todo_tasks.append(task)
    todo_tasks = sorted(todo_tasks, key=lambda t: t.optional)
    if serialized:
        return json.loads(serializers.serialize("json", todo_tasks))
    return todo_tasks

def get_all_repeating_data():
    data = {}
    for spec in ("today", "tomorrow", "all"):
        data[spec] = json.loads(serializers.serialize("json", get_repeating_data(spec)))
    return data

class Task(models.Model):
    WEEKDAYS = (
        ("ma", "maanantai"),
        ("ti", "tiistai"),
        ("ke", "keskiviikko"),
        ("to", "torstai"),
        ("pe", "perjantai"),
        ("la", "lauantai"),
        ("su", "sunnuntai"),
    )

    title = models.TextField(verbose_name="Otsikko") #TODO: convert to CharField
    optional = models.NullBooleanField(default=False, verbose_name="Optionaalinen", help_text="Kyllä, jos tarkoituksena on tarkistaa, eikä tehdä joka kerta.")
    snooze = models.DateTimeField(null=True, blank=True)
    repeat_every_n_seconds = models.IntegerField(null=True, blank=True, verbose_name="Toista joka n:s sekunti", help_text="Toistoväli sekunteina")
    trigger_every_weekday = models.CharField(null=True, blank=True, max_length=2, choices=WEEKDAYS, verbose_name="Toista tiettynä viikonpäivänä")
    trigger_every_day_of_month = models.SmallIntegerField(null=True, blank=True, verbose_name="Toista tiettynä päivänä kuukaudesta")
    last_completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Edellinen valmistuminen", help_text="Edellinen kerta kun tehtävä on tehty")

    class Meta:
        verbose_name = "Toistuva tehtävä"
        verbose_name_plural = "Toistuvat tehtävät"

    def time_since_completion(self):
        """ Returns datetime.timedelta for time since last completion.
            None if never completed.
        """
        if self.last_completed_at is None:
            return None
        return now() - self.last_completed_at

    def expires_at(self):
        """ Returns datetime when this task expires """
        if self.snooze:
            return self.snooze
        if self.last_completed_at is None:
            return now()
        # TODO: this does not work properly with other triggering options
        exact_expiration = self.last_completed_at + datetime.timedelta(seconds=self.repeat_every_n_seconds)
        if exact_expiration < now():
            return now()
        return exact_expiration


    def overdue_by(self):
        """ Returns overdue in datetime.timedelta.
            < 0 if task is not overdue
            > 0 if task is overdue

        """
        if self.snooze:
            if self.snooze < now():
                self.snooze = None
                self.save()
            else:
                return now() - self.snooze
        tsc = self.time_since_completion()
        if tsc is None:
            return datetime.timedelta(0)
        # TODO: this does not work properly with other triggering options
        return self.time_since_completion() - datetime.timedelta(seconds=self.repeat_every_n_seconds)

    def snooze_by(self, days):
        """ Add specified snoozing time to Task. """
        if not self.snooze:
            self.snooze = now()
        self.snooze += datetime.timedelta(days=days)
        self.save()

    def completed(self):
        n = now()
        self.last_completed_at = n
        self.snooze = None
        a = TaskHistory(task=self, completed_at=n)
        a.save()
        self.save()

    def undo_completed(self):
        try:
            latest = TaskHistory.objects.filter(task=self).latest()
            latest.delete()
            latest = TaskHistory.objects.filter(task=self).latest()
            self.last_completed_at = latest.completed_at
            self.save()
            return True
        except TaskHistory.DoesNotExist:
            return False

    def __unicode__(self):
        #TODO: this does not work properly with other triggering options
        return u"%s (%sd)" % (self.title, self.repeat_every_n_seconds / 86400)

class TaskHistory(models.Model):
    class Meta:
        get_latest_by = "completed_at"

    task = models.ForeignKey("Task")
    completed_at = models.DateTimeField(null=True)

def publish_changes():
    for k in ("today", "tomorrow", "all"):
        publish_ws("repeating_tasks_%s" % k, get_repeating_data(k, True))


@receiver(post_delete, sender=Task, dispatch_uid='task_delete_signal')
def publish_task_deleted(sender, instance, using, **kwargs):
    publish_changes()

@receiver(post_save, sender=Task, dispatch_uid="task_saved_signal")
def publish_task_saved(sender, instance, *args, **kwargs):
    publish_changes()
