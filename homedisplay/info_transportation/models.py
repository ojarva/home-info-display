from django.db import models

class Stop(models.Model):
    description = models.CharField(max_length=50)
    stop_number = models.CharField(max_length=20)

class Line(models.Model):
    stop = models.ForeignKey("Stop")
    line_number = models.CharField(max_length=20)
