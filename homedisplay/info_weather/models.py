from django.db import models

def convert_wind_direction_degrees(wind_direction):
    direction = None
    weight = 0
    for c in wind_direction:
        if c == "N": # Special case
            if "E" in wind_direction:
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
        return convert_wind_direction_degrees(self.wind_direction)

class MarineDataPoint(models.Model):
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=50)
    forecast = models.BooleanField(blank=True, default=False)

    air_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    water_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wave_direction = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wave_dispersion = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wave_height = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wave_period = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wind_direction = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wind_gusts = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wind_max = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = ("timestamp", "location")
        ordering = ("-timestamp", )
        get_latest_by = "timestamp"

    def __unicode__(self):
        return u"%s - %s (forecast=%s)" % (self.location, self.timestamp, self.forecast)
