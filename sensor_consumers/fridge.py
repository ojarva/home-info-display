# coding=utf-8

from utils import SensorConsumerBase
import datetime
import sys


class Fridge(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")

    def run(self):
        self.subscribe("fridgetop-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        self.insert_into_influx([{
            "measurement": "fridge",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "power_consumption": round(data["data"]["power_consumption"], 3),
                "kitchen_ceiling_temperature": round(data["data"]["room_temperature"], 1),
            }
        }])


def main():
    item = Fridge()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
