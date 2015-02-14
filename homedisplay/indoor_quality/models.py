from django.db import models
import redis
import json

redis_instance = redis.StrictRedis()

class AirDataPoint(models.Model):
    timepoint = models.ForeignKey("AirTimePoint")
    name = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    class Meta:
        ordering = ["-timepoint__timestamp"]
        get_latest_by = "-timepoint__timestamp"

    def save(self, *args, **kwargs):
        redis_collect_key = "air-collect-%s" % self.name
        redis_storage_key = "air-storage-%s" % self.name
        redis_instance.lpush(redis_collect_key, self.value)
        if self.timepoint.timestamp.minute % 5 == 0:
            # Calculate average every five minutes
            old_values = redis_instance.lrange(redis_collect_key, 0, -1)
            redis_instance.delete(redis_collect_key)
            final_values = []
            for item in old_values:
              try:
                final_values.append(float(item))
              except ValueError:
                pass
            if len(final_values) > 0:
              value = float(sum(final_values)) / len(final_values)
            else:
              value = None

            redis_instance.lpush(redis_storage_key, json.dumps({"timestamp": str(self.timepoint.timestamp), "value": value}))
            redis_instance.ltrim(redis_storage_key, 0, 288)
        super(AirDataPoint, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s - %s=%s" % (self.timepoint.timestamp, self.name, self.value)

class AirTimePoint(models.Model):
    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "-timestamp"

    def __unicode__(self):
        return self.timestamp

    timestamp = models.DateTimeField(auto_now_add=True)
