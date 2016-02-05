# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class Freezer(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.door_open_since = None
        self.temperature_too_high_since = None
        self.delete_notification("freezer-door")
        self.delete_notification("freezer-temperature")

    def run(self):
        self.subscribe("freezer-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        door_open = int(data["data"]["door"]) == 0

        self.insert_into_influx([{
            "measurement": "freezer",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "power_consumption": round(data["data"]["power_consumption"], 3),
                "door": door_open,
                "temperature1": round(data["data"]["temperature1"], 1),
                "temperature2": round(data["data"]["temperature2"], 1),
                "water": data["data"]["water"],
            }
        }])

        temperature = round(data["data"]["temperature1"], 1)
        if temperature > - 10:
            if self.temperature_too_high_since is None:
                self.temperature_too_high_since = datetime.datetime.now()
            level = "normal"
            if datetime.datetime.now() - self.temperature_too_high_since > datetime.timedelta(minutes=30):
                level = "high"
            self.update_notification("freezer-temperature", "Iso pakastin liian lämmin: %s ({elapsed_since})" % temperature, False, elapsed_since=self.temperature_too_high_since, level=level)
        else:
            self.temperature_too_high_since = None
            self.delete_notification("freezer-temperature")

        if door_open:
            if self.door_open_since is None:
                self.door_open_since = datetime.datetime.now()
            level = "normal"
            if datetime.datetime.now() - self.door_open_since > datetime.timedelta(seconds=15):
                level = "high"
            self.update_notification("freezer-door", "Ison pakastimen ovi auki ({elapsed_since})", False, elapsed_since=self.door_open_since, level="level")
        else:
            if self.door_open_since:
                self.door_open_since = None
                self.delete_notification("freezer-door")


def main():
    item = Freezer()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
