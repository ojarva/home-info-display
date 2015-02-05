from django.db import models
from django.utils.timezone import now
import datetime

class Task(models.Model):
    title = models.TextField()
    repeat_every_n_seconds = models.IntegerField()
    last_completed_at = models.DateTimeField(null=True, blank=True)

    def time_since_completion(self):
        if self.last_completed_at is None:
            return None
        return now() - self.last_completed_at

    def overdue_by(self):
        tsc = self.time_since_completion()
        if tsc is None:
            return datetime.timedelta(0)
        return self.time_since_completion() - datetime.timedelta(seconds=self.repeat_every_n_seconds)

    def completed(self):
        n = now()
        self.last_completed_at = n
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
        return u"%s (%sd)" % (self.title, (self.repeat_every_n_seconds / 86400))

class TaskHistory(models.Model):
    class Meta:
        get_latest_by = "completed_at"

    task = models.ForeignKey("Task")
    completed_at = models.DateTimeField(null=True)
