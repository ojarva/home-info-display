from django.db import models

# Create your models here.


class KettleSchedule(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    pass
