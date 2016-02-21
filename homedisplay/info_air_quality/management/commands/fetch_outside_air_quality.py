from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from homedisplay.utils import publish_ws
from influxdb import InfluxDBClient
from info_air_quality.models import OutsideAirQuality
import datetime
import influxdb.exceptions
import json
import redis
import requests


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class Command(BaseCommand):
    args = ''
    help = 'Fetches outdoor air quality information'

    def handle(self, *args, **options):
        items = [
            "particulateslt10um",
            "ozone",
            "particulateslt2.5um",
            "sulphurdioxide",
            "nitrogendioxide",
        ]

        date = datetime.date.today().strftime("%d.%m.%Y")

        session = requests.Session()
        latest_values = {}

        influx_datapoints = []
        headers = {
            "Accept-Encoding": None,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36",
        }


        for quality_item in items:

            url = "http://www.ilmanlaatu.fi/ilmanyt/nyt/ilmanyt.php?as=Suomi&rs=86&ss=425&p={sensor}&pv={date}&j=23&et=table&tj=3600&ls=suomi".format(sensor=quality_item, date=date)
            session.get(url)

            url_table = "http://www.ilmanlaatu.fi/php/table/observationsInTable.php?step=3600&today=1&timesequence=23&time=%s&station=425" % datetime.datetime.now().strftime("%Y%m%d%H")

            headers["referer"] = url
            response = session.get(url_table, headers=headers)
            soup = BeautifulSoup(response.text, "lxml")
            value = None
            timestamp = None
            for row in soup.table.find_all("tr"):
                try:
                    c = row["class"]
                    if "sinitausta" in c:
                        # Header row
                        continue
                except KeyError:
                    pass

                current_hour = None
                for item in row.find_all("td"):
                    if current_hour is None:
                        current_hour = int(item.string)
                        if current_hour > 23:
                            current_hour = False
                            continue
                    elif current_hour is not False:
                        try:
                            value = float(item.string)
                        except TypeError:
                            continue

                        timestamp = timezone.make_aware((datetime.datetime.combine(datetime.date.today(), datetime.time(current_hour, 0))), timezone.get_current_timezone())

                        item, _ = OutsideAirQuality.objects.get_or_create(type=quality_item, timestamp=timestamp, defaults={"value": value})
                        item.value = value

                        influx_datapoints.append({
                            "measurement": "outside_air_quality",
                            "tags": {
                                "measurement": quality_item,
                                "location": "Kallio",
                            },
                            "time": timestamp.isoformat(),
                            "fields": {
                                "value": value,
                            },
                        })
                        item.save()
            if value is not None and timestamp is not None:
                latest_values[quality_item] = {"timestamp": str(timestamp), "value": value}
        if len(influx_datapoints) > 0:
            print influx_datapoints
            redis_instance = redis.StrictRedis()
            redis_instance.publish("influx-update-pubsub", json.dumps(influx_datapoints, cls=DateTimeEncoder))
            influx_client = InfluxDBClient("localhost", 8086, "root", "root", "home")

            try:
                influx_client.create_database("home")
            except influxdb.exceptions.InfluxDBClientError:
                pass
            influx_client.write_points(influx_datapoints)
        publish_ws("outside_air_quality", latest_values)
