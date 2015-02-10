from django.db import models

class IndoorQuality(models.Model):
    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "-timestamp"

    timestamp = models.DateTimeField(auto_now_add=True)
    co2 = models.IntegerField(null=True)
    temperature = models.DecimalField(max_digits=6, decimal_places=2)

class AirDataPoint(models.Model):
    timepoint = models.ForeignKey("AirTimePoint")
    name = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=7, decimal_places=2, null=True)

class AirTimePoint(models.Model):
    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "-timestamp"

    timestamp = models.DateTimeField(auto_now_add=True)
