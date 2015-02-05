from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from info_internet_connection.models import Internet
import datetime
import huawei_b593_status
import redis

r = redis.StrictRedis()

#{'WIFI': 'off', 'SIG': '5', 'Mode': '4g', 'Roam': 'home', 'SIM': 'normal', 'Connect': 'connected'}


class Command(BaseCommand):
    args = ''
    help = 'Fetches home 4g router status information'

    def handle(self, *args, **options):
        status = huawei_b593_status.HuaweiStatus()
        data = status.read()
        age_threshold = datetime.timedelta(minutes=2)

        try:
            latest_data = Internet.objects.latest()
            if now() - latest_data.timestamp > age_threshold:
                latest_data = Internet()
        except Internet.DoesNotExist:
            latest_data = Internet()

        latest_data.wifi = data["WIFI"] != "off"
        latest_data.signal = int(data["SIG"])
        latest_data.mode = data["Mode"]
        latest_data.sim = data["SIM"]
        latest_data.connect_status = data["Connect"]
        latest_data.update_timestamp = now()
        latest_data.save()
        r.publish("home:broadcast:internet", "updated")
