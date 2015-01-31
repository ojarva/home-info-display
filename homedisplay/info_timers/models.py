from django.db import models
import datetime

class Timer(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.IntegerField(null=True)
    running = models.NullBooleanField(default=True)
    stopped_at = models.DateTimeField(null=True)

    @property
    def end_time(self):
        if self.duration:
            return self.start_time + datetime.timedelta(seconds=self.duration)
