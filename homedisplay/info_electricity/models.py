from django.db import models

class Electricity(models.Model):

    class Meta:
        unique_together = (("date", "hour"))
        ordering = ["date", "hour"]

    date = models.DateField()
    hour = models.PositiveSmallIntegerField()

    usage = models.DecimalField(max_digits=10, decimal_places=2)

class Note(models.Model):
    hour = models.ForeignKey("Electricity")
    note = models.TextField()
