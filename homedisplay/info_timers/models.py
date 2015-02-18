from django.db import models
from django.utils.timezone import now
from django.core import serializers
import datetime
import json


def get_serialized_timer(item):
    return json.loads(serializers.serialize("json", [item]))

class Timer(models.Model):
    name = models.CharField(max_length=30)
    start_time = models.DateTimeField()
    duration = models.IntegerField(null=True)
    running = models.NullBooleanField(default=True)
    stopped_at = models.DateTimeField(null=True)
    action = models.CharField(max_length=50, null=True)

    @property
    def end_time(self):
        if self.duration:
            return self.start_time + datetime.timedelta(seconds=self.duration)
        return now()
