from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from homedisplay.utils import publish_ws
from influxdb import InfluxDBClient
import datetime
import influxdb.exceptions
import json
import redis
import requests


class DateTimeEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class Command(BaseCommand):
    args = ''
    help = 'Fetches outdoor air quality information'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.redis_instance = redis.StrictRedis()
        self.influx_client = InfluxDBClient(
            "localhost", 8086, "root", "root", "home")
        try:
            self.influx_client.create_database("home")
        except influxdb.exceptions.InfluxDBClientError:
            pass

    def save_to_influx(self, datapoints):
        self.redis_instance.publish(
            "influx-update-pubsub", json.dumps(datapoints, cls=DateTimeEncoder))
        self.influx_client.write_points(datapoints)

    def get_data(self, station_id, sensor):
        session = requests.Session()
        headers = {
            "Accept-Encoding": None,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36",
        }
        date = datetime.date.today().strftime("%d.%m.%Y")
        url = "http://www.ilmanlaatu.fi/ilmanyt/nyt/ilmanyt.php?as=Suomi&rs=86&ss={station_id}&p={sensor}&pv={date}&j=23&et=table&tj=3600&ls=suomi".format(
            sensor=sensor, date=date, station_id=station_id)
        session.get(url)

        url_table = "http://www.ilmanlaatu.fi/php/table/observationsInTable.php?step=3600&today=1&timesequence=23&time={timestamp}&station={station_id}".format(
            timestamp=datetime.datetime.now().strftime("%Y%m%d%H"), station_id=station_id)

        headers["referer"] = url
        return session.get(url_table, headers=headers).text

    def process_station(self, station_config):
        influx_datapoints = []
        latest_values = {}
        for quality_item in station_config["sensors"]:
            response_text = self.get_data(
                station_config["station_id"], quality_item)
            soup = BeautifulSoup(response_text, "lxml")
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

                        timestamp = timezone.make_aware((datetime.datetime.combine(datetime.date.today(
                        ), datetime.time(current_hour, 0))), timezone.get_current_timezone())

                        if station_config["station_name"] == "Kallio":
                            self.redis_instance.setex(
                                "outdoor-air-quality-latest-%s" % quality_item, 3600 * 6, value)
                        influx_datapoints.append({
                            "measurement": "outside_air_quality",
                            "tags": {
                                "measurement": quality_item,
                                "location": station_config["station_name"],
                            },
                            "time": timestamp.isoformat(),
                            "fields": {
                                "value": value,
                            },
                        })
            if value is not None and timestamp is not None and station_config["station_name"] == "Kallio":
                latest_values[quality_item] = {
                    "timestamp": str(timestamp), "value": value}

        if len(influx_datapoints) > 0:
            self.save_to_influx(influx_datapoints)
        if station_config["station_name"] == "Kallio":
            publish_ws("outside_air_quality", latest_values)

    def handle(self, *args, **options):
        stations = [
            {
                "station_id": "425",
                "station_name": "Kallio",
                "sensors": ["particulateslt10um", "ozone", "particulateslt2.5um", "sulphurdioxide", "nitrogendioxide"],
            },
            {
                "station_id": "781",
                "station_name": "Vartiokyla",
                "sensors": ["ozone", "particulateslt2.5um", "nitrogendioxide"],
            },
            {
                "station_id": "564",
                "station_name": "Mannerheimintie",
                "sensors": ["particulateslt10um", "particulateslt2.5um", "nitrogendioxide"],
            },
            {
                "station_id": "902",
                "station_name": "Makelankatu",
                "sensors": ["particulateslt10um", "ozone", "particulateslt2.5um", "nitrogendioxide"],
            }
        ]

        for station_config in stations:
            self.process_station(station_config)
