from django.db import models

class LightState(models.Model):
    group = models.PositiveSmallIntegerField(primary_key=True)
    rgbw_brightness = models.PositiveSmallIntegerField(null=True)
    white_brightness = models.PositiveSmallIntegerField(null=True)
    color = models.TextField(null=True, blank=True)
    on = models.NullBooleanField(null=True)
