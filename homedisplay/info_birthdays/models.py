from django.db import models
from django.utils.timezone import now
from django.db.models.signals import pre_delete
from django.db.models.signals import post_save

from django.dispatch import receiver
import redis
r = redis.StrictRedis()

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

@receiver(pre_delete, sender=Birthday, dispatch_uid='birthday_delete_signal')
def publish_birthday_deleted(sender, instance, using, **kwargs):
    r.publish("home:broadcast:birthdays", "updated")

@receiver(post_save, sender=Birthday, dispatch_uid="birthday_saved_signal")
def publish_birthday_saved(sender, instance, *args, **kwargs):
    r.publish("home:broadcast:birthdays", "updated")
