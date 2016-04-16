import json
from django.db import models
from django.core import serializers


def get_latest_serialized():
    try:
        item = [Internet.objects.latest()]
    except Internet.DoesNotExist:
        return {"status": "error", "message": "No data available"}
    return json.loads(serializers.serialize("json", item))[0]


class Internet(models.Model):

    class Meta:  # pylint:disable=no-init,too-few-public-methods,old-style-class
        get_latest_by = "timestamp"

    MODES = (("off", "off"),
             ("2g", "2g"),
             ("3g", "3g"),
             ("4g", "4g"),
             ("sim_disabled", "sim_disabled"))

    CONNECT_MODES = (("no_connect", "no_connect"),
                     ("connecting", "connecting_now"),
                     ("connected", "connected"))

    SIM_MODES = (("no_sim", "No SIM installed"),
                 ("normal", "normal"),
                 ("pin_locked", "requires PIN"),
                 ("error", "error"))

    timestamp = models.DateTimeField(auto_now_add=True)
    update_timestamp = models.DateTimeField(null=True)
    wifi = models.NullBooleanField(null=True)
    signal = models.PositiveSmallIntegerField(null=True)
    mode = models.CharField(
        max_length=12, choices=MODES, null=True, blank=True)
    sim = models.CharField(
        max_length=12, choices=SIM_MODES, null=True, blank=True)
    connect_status = models.CharField(
        max_length=12, choices=CONNECT_MODES, null=True, blank=True)


class MacDb(models.Model):
    mac = models.CharField(max_length=17, unique=True)
    hostname = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return u""


class ConnectedClient(models.Model):
    mac = models.CharField(max_length=17, unique=True)
    rssi = models.IntegerField(null=True, blank=True)
    bandwidth_in = models.IntegerField(null=True, blank=True)
    bandwidth_out = models.IntegerField(null=True, blank=True)
    tx = models.BigIntegerField(null=True, blank=True)  # pylint:disable=invalid-name
    rx = models.BigIntegerField(null=True, blank=True)  # pylint:disable=invalid-name

    def __unicode__(self):
        return self.mac
