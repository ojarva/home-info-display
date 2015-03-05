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
