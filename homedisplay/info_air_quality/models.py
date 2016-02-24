from django.db import models


class OutsideAirQuality(models.Model):
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=40)
    value = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"
        unique_together = ("timestamp", "type")

    def __unicode__(self):
        return u"%s @ %s : %s" % (self.type, self.timestamp, self.value)
