from django.db import models


class MarineDataPoint(models.Model):
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=50)
    forecast = models.BooleanField(blank=True, default=False)

    air_temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    water_temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wave_direction = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wave_dispersion = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wave_height = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wave_period = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wind_direction = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wind_gusts = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wind_max = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)
    wind_speed = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = ("timestamp", "location")
        ordering = ("-timestamp", )
        get_latest_by = "timestamp"

    def __unicode__(self):
        return u"%s - %s (forecast=%s)" % (self.location, self.timestamp, self.forecast)
