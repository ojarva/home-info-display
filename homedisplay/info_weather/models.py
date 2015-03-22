from django.db import models

class Weather(models.Model):
    class Meta:
        unique_together = (("date", "hour"))
        ordering = ["date", "hour"]


    def __unicode__(self):
        return u"%s - %s" % (self.date, self.hour)

    date = models.DateField()
    hour = models.PositiveSmallIntegerField()

    icon = models.TextField()
    ppcp = models.PositiveSmallIntegerField()
    dewpoint = models.IntegerField()
    feels_like = models.IntegerField()
    humidity = models.PositiveSmallIntegerField()
    temperature = models.IntegerField()

    description = models.TextField()

    wind_direction = models.TextField()
    wind_gust = models.TextField()
    wind_speed = models.IntegerField()

    uv = models.IntegerField(null=True, blank=True)

    def get_wind_direction_degrees(self):
        direction = None
        weight = 0
        for c in self.wind_direction:
            if c == "N": # Special case
                if "E" in self.wind_direction:
                    cur = 0.0
                else:
                    cur = 360.0
            elif c == "E":
                cur = 90.0
            elif c == "S":
                cur = 180.0
            elif c == "W":
                cur = 270.0
            weight += 1
            if direction is None:
                # First direction
                direction = cur
                continue
            direction += (cur - direction) / 2
        return direction
