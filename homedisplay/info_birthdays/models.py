from django.db import models
from django.utils.timezone import now

class Birthday(models.Model):
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, null=True, blank=True)
    birthday = models.DateField()
    valid_year = models.NullBooleanField(null=True, default=True)

    @property
    def age(self):
        diff = now() - self.birthday
        return int(diff.days / 365.2425)

    def __unicode__(self):
        return u"%s (%s) %s (valid_year=%s)" % (self.name, self.nickname, self.birthday, self.valid_year)

    class Meta:
        ordering = ["name"]
