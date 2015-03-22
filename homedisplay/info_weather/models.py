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

    wind_direction = models.CharField(max_length=4)
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

class MarineWeather(models.Model):
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=30)
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    dewpoint = models.DecimalField(max_digits=4, decimal_places=1)
    humidity = models.DecimalField(max_digits=4, decimal_places=1)
    cloudiness = models.PositiveSmallIntegerField()
    visibility = models.IntegerField()
    pressure = models.DecimalField(max_digits=5, decimal_places=1)

    wind_direction = models.CharField(max_length=4)
    wind_speed = models.IntegerField()
    wind_gust = models.IntegerField()

    class Meta:
        unique_together = ("timestamp", "location")
        ordering = ("-timestamp",)
        get_latest_by = "-timestamp"

    def __unicode__(self):
        return u"%s @ %s" % (self.location, self.timestamp)
