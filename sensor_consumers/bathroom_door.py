# coding=utf-8

from setproctitle import setproctitle
from utils import SensorConsumerBase
import os
import sys


class Bathroom(SensorConsumerBase):

    def __init__(self, redis_host, redis_port):
        SensorConsumerBase.__init__(self, redis_host=redis_host, redis_port=redis_port)

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

        if bathroom_temperature < 1 or bathroom_temperature > 60:
            bathroom_temperature = None
        if corridor_temperature < 1 or corridor_temperature > 60:
            corridor_temperature = None

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
    setproctitle("bathroom-door: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    item = Bathroom(redis_host, redis_port)
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
