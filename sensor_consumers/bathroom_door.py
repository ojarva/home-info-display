# coding=utf-8

from utils import SensorConsumerBase
import sys


class Bathroom(SensorConsumerBase):

    def __init__(self):
        SensorConsumerBase.__init__(self)

    def run(self):
        self.subscribe("bathroom-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            # if data["action"] == "user_dismissed":
            return

        bathroom_temperature = round(data["data"]["bathroom_temperature"], 1)
        bathroom_humidity = round(data["data"]["bathroom_humidity"], 1)
        corridor_temperature = round(data["data"]["corridor_temperature"], 1)
        corridor_humidity = round(data["data"]["corridor_humidity"], 1)

        if bathroom_temperature < 5 or bathroom_temperature > 60:
            bathroom_temperature = None
        if corridor_temperature < 5 or corridor_temperature > 60:
            corridor_temperature = None
        if bathroom_humidity < 5 or bathroom_humidity > 100:
            bathroom_humidity = None
        if corridor_humidity < 5 or corridor_humidity > 100:
            corridor_humidity = None

        influx_data = {
            "measurement": "bathroom",
            "time": data["utctimestamp"].isoformat() + "Z",
            "tags": {
                "location": "bathroom-door",
            },
            "fields": {
                "distance_reading": data["data"]["distance_reading"],
                "bathroom_temperature": bathroom_temperature,
                "bathroom_humidity": bathroom_humidity,
                "corridor_temperature": corridor_temperature,
                "corridor_humidity": corridor_humidity,
            },
        }
        self.insert_into_influx([influx_data])


def main():
    item = Bathroom()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
