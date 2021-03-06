# coding=utf-8

from setproctitle import setproctitle
from utils import SensorConsumerBase
import json
import os
import sys


class DustNode(SensorConsumerBase):

    def __init__(self, redis_host, redis_port):
        SensorConsumerBase.__init__(self, redis_host=redis_host, redis_port=redis_port)

    def run(self):
        self.subscribe("dust-node-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        room_temperature = round(data["data"]["room_temperature"], 1)
        room_humidity = round(data["data"]["room_humidity"], 1)

        if room_temperature > 50 or room_temperature < 1:
            room_temperature = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "dustnode", "name": "room", "value": room_temperature}))

        if room_humidity < 0 or room_humidity > 100:
            room_temperature = None
        else:
            self.redis_instance.publish("humidity-pubsub", json.dumps({"source": "dustnode", "name": "room", "value": room_temperature > 100}))

        influx_data = {
            "measurement": "dustnode",
            "time": data["utctimestamp"].isoformat() + "Z",
            "fields": {
                "room_humidity": room_humidity,
                "room_temperature": room_temperature,
                "barometer_temperature": round(data["data"]["barometer_temperature"], 1),
                "barometer_pressure": round(data["data"]["barometer_reading"], 1),
                "sound_level": data["data"]["sound_level"],
            }
        }
        self.insert_into_influx([influx_data])
        self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_temperature", "content": {"value": room_temperature}}))
        self.redis_instance.setex("air-latest-temperature", 300, room_temperature)
        self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_humidity", "content": {"value": room_humidity}}))
        self.redis_instance.setex("air-latest-humidity", 300, room_humidity)


def main():
    setproctitle("indoor-air-quality-node: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    item = DustNode(redis_host, redis_port)
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
