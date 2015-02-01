from django.db import models

class IndoorQuality(models.Model):
    class Meta:
        ordering = ["timestamp"]
        get_latest_by = "timestamp"

    timestamp = models.DateTimeField(auto_now_add=True)
    co2 = models.IntegerField(null=True)
    temperature = models.DecimalField(max_digits=6, decimal_places=2)
