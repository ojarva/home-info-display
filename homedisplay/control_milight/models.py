from django.db import models

class LightState(models.Model):
    group = models.PositiveSmallIntegerField(primary_key=True)
    rgbw_brightness = models.PositiveSmallIntegerField(null=True)
    white_brightness = models.PositiveSmallIntegerField(null=True)
    color = models.TextField(null=True, blank=True)
    on = models.NullBooleanField(null=True)

class LightTransition(models.Model):
    group = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.PositiveSmallIntegerField(default=0)
    start_brightness = models.PositiveSmallIntegerField(null=True)
    to_brightness = models.PositiveSmallIntegerField(null=True)
    to_nightmode = models.NullBooleanField(null=True)
    to_color = models.TextField(null=True, blank=True)
