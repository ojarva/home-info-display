from django.db import models
import redis
import json

redis_instance = redis.StrictRedis()

class AirDataPoint(models.Model):
    """ This represents a single sensor datapoint.
        Timestamps for readings are syncronized with
        AirTimePoint models. AirTimePoint rows should/could
        be created with add_air_timepoint management command.

        save() will also store latest reading and automatically
        calculate 5min aggregates to redis. These readings are
        used by nvd3 graphs.
    """
    timepoint = models.ForeignKey("AirTimePoint")
    name = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    class Meta:
        ordering = ["-timepoint__timestamp"]
        get_latest_by = "-timepoint__timestamp"

    def save(self, *args, **kwargs):
        redis_latest_key = "air-latest-%s" % self.name
        redis_collect_key = "air-collect-%s" % self.name
        redis_storage_key = "air-storage-%s" % self.name
        redis_instance.setex(redis_latest_key, 300, self.value)
        redis_instance.lpush(redis_collect_key, self.value)
        if self.timepoint.timestamp.minute % 5 == 0:
            # Calculate average every five minutes
            old_values = redis_instance.lrange(redis_collect_key, 0, -1)
            redis_instance.delete(redis_collect_key)
            final_values = []
            for item in old_values:
                try:
                    final_values.append(float(item))
                except (ValueError, TypeError):
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
    """ This represents syncronized time point for each sensor's data.
        New TimePoints should be created regularly - i.e. with cron -
        using add_air_timepoint management command.
    """

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "-timestamp"

    def __unicode__(self):
        return self.timestamp

    timestamp = models.DateTimeField(auto_now_add=True)
