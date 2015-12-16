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

    def run(self):
        self.subscribe("freezer-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        door_open = int(data["data"]["door"]) == 1

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

        if door_open:
            self.door_open_since = datetime.datetime.now()
            self.update_notification("freezer", "Ison pakastimen ovi auki ({elapsed_since})", False, elapsed_since=self.door_open_since)
        else:
            if self.door_open_since:
                self.door_open_since = None
                self.delete_notification("freezer")


def main():
    item = Freezer()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
