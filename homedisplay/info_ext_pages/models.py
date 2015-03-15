from django.db import models

class ExtPage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=1024)

    def __unicode__(self):
        return u"%s" % self.url

    class Meta:
        ordering = ("timestamp", )
        verbose_name = "Osoite"
        verbose_name_plural = "Osoitteet"
        get_latest_by = "timestamp"
