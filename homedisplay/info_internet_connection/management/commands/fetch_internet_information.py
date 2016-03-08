from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from homedisplay.utils import publish_ws
from influxdb import InfluxDBClient
from info_internet_connection.models import Internet, get_latest_serialized
import datetime
import huawei_b593_status
import json
import redis


# {'WIFI': 'off', 'SIG': '5', 'Mode': '4g', 'Roam': 'home', 'SIM': 'normal', 'Connect': 'connected'}

class DateTimeEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class Command(BaseCommand):
    args = ''
    help = 'Fetches home 4g router status information'

    def handle(self, *args, **options):
        modes = {
            "sim_disabled": -1,
            "off": 0,
            "2g": 1,
            "3g": 2,
            "4g": 3,
        }

        status = huawei_b593_status.HuaweiStatus()
        data = status.read()
        age_threshold = datetime.timedelta(minutes=2)

        try:
            latest_data = Internet.objects.latest()
            if timezone.now() - latest_data.timestamp > age_threshold:
                latest_data = Internet()
        except Internet.DoesNotExist:
            latest_data = Internet()

        latest_data.wifi = data["WIFI"] != "off"
        latest_data.signal = int(data["SIG"])
        latest_data.mode = data["Mode"]
        latest_data.sim = data["SIM"]
        latest_data.connect_status = data["Connect"]
        latest_data.update_timestamp = timezone.now()
        latest_data.save()

        influx_data = [{
            "timestamp": timezone.now().isoformat(),
            "measurement": "modem",
            "tags": {
                "device": "home-gw",
            },
            "fields": {
                "wifi": data["WIFI"] != "off",
                "signal": int(data["SIG"]),
                "mode": data["Mode"],
                "mode_number": modes.get(data["Mode"]),
                "sim": data["SIM"],
                "connect_status": data["Connect"],
            },
        }]
        redis_instance = redis.StrictRedis()
        redis_instance.publish("influx-update-pubsub", json.dumps(influx_data, cls=DateTimeEncoder))
        publish_ws("internet", get_latest_serialized())

        influx_client = InfluxDBClient("localhost", 8086, "root", "root", "home")
        influx_client.write_points(influx_data)
