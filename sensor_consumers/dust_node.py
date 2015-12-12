# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class DustNode(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")

    def run(self):
        self.subscribe("dust-node-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        influx_data = {
            "measurement": "dustnode",
            "timestamp": data["utctimestamp"].isoformat() + "Z",
            "fields": {
                "room_humidity": data["data"]["room_humidity"],
                "room_temperature": round(data["data"]["room_temperature"], 1),
                "barometer_temperature": round(data["data"]["barometer_temperature"], 1),
                "barometer_pressure": round(data["data"]["barometer_reading"], 1),
                "dust_density": round(data["data"]["dust_density"], 5)
            }
        }
        self.insert_into_influx([influx_data])


def main():
    item = DustNode()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
