# coding=utf-8

from utils import SensorConsumerBase
import sys


class Bathroom(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "home")

    def run(self):
        self.subscribe("bathroom-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            # if data["action"] == "user_dismissed":

            return

        influx_data = {
            "measurement": "bathroom",
            "timestamp": data["utctimestamp"].isoformat() + "Z",
            "tags": {
                "location": "bathroom-door",
            }
            "fields": {
                "distance_reading": data["data"]["distance_reading"],
                "bathroom_temperature": round(data["data"]["bathroom_temperature"], 1),
                "bathroom_humidity": round(data["data"]["bathroom_humidity"], 1),
                "corridor_temperature": round(data["data"]["corridor_temperature"], 1),
                "corridor_humidity": round(data["data"]["corridor_humidity"], 1)
            }
        }
        self.insert_into_influx([influx_data])


def main():
    item = Bathroom()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
