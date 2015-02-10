from django.db import models
from django.utils.timezone import now
import datetime

class ActionTimer(models.Model):
    name = models.CharField(max_length=25)
    start_time = models.DateTimeField()
    duration = models.IntegerField(null=True)
    action = models.CharField(max_length=100)
    delay_until = models.CharField(max_length=100)

    @property
    def end_time(self):
        if self.duration:
            return self.start_time + datetime.timedelta(seconds=self.duration)
        return now()
