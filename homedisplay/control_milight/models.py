from django.db import models
from ledcontroller import LedController
from django.conf import settings


__all__ = ["LightGroup", "LightTransition"]

led = LedController(settings.MILIGHT_IP)

class LightGroup(models.Model):
    group_id = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    rgbw_brightness = models.PositiveSmallIntegerField(null=True)
    white_brightness = models.PositiveSmallIntegerField(null=True)
    color = models.TextField(null=True, blank=True)
    on = models.NullBooleanField(null=True)

    def __unicode__(self):
        return "%s (%s), color: %s, on: %s, rgbw: %s, white: %s" % (self.description, self.group_id, self.color, self.on, self.rgbw_brightness, self.white_brightness)

    def set_state(self, brightness, color=None, on=True):
        if brightness is not None:
            if color == "white":
                self.white_brightness = brightness
            else:
                self.rgb_brightness = brightness
        if color is not None:
            self.color = color
        self.on = on
        self.save()
        return self


class LightTransition(models.Model):
    group = models.ForeignKey("LightGroup")
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.PositiveSmallIntegerField(default=0)
    start_brightness = models.PositiveSmallIntegerField(null=True)
    to_brightness = models.PositiveSmallIntegerField(null=True)
    to_nightmode = models.NullBooleanField(null=True)
    to_color = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s (%s): %s->%s" % (self.group.group_id, self.description, self.start_brightness, self.to_brightness)

class LightAutomation(models.Model):
    action = models.CharField(max_length=30)
    start_time = models.TimeField()
    duration = models.IntegerField()
