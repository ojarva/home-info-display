# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class Bathroom(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "bathroom")

    def run(self):
        self.subscribe("bathroom-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
#            if data["action"] == "user_dismissed":

            return

        influx_data = {
            "measurement": "bathroom",
            "timestamp": data["utctimestamp"].isoformat() + "Z",
            "fields": {
                "distance_reading": data["data"]["distance_reading"],
                "bathroom_temperature": data["data"]["bathroom_temperature"],
                "bathroom_humidity": data["data"]["bathroom_humidity"],
                "corridor_temperature": data["data"]["corridor_temperature"],
                "corridor_humidity": data["data"]["corridor_humidity"]
            }
        }
        self.insert_into_influx([influx_data])

def main():
    item = Bathroom()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
