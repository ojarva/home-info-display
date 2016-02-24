# coding=utf-8

from utils import SensorConsumerBase
import sys


class DustNode(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "home")

    def run(self):
        self.subscribe("dust-node-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        room_temperature = round(data["data"]["room_temperature"], 1)

        influx_data = {
            "measurement": "dustnode",
            "timestamp": data["utctimestamp"].isoformat() + "Z",
            "fields": {
                "room_humidity": round(data["data"]["room_humidity"], 1),
                "room_temperature": room_temperature,
                "barometer_temperature": round(data["data"]["barometer_temperature"], 1),
                "barometer_pressure": round(data["data"]["barometer_reading"], 1),
                "sound_level": data["data"]["sound_level"],
            }
        }
        self.insert_into_influx([influx_data])
        self.redis_instance.publish("home:broadcast:generic", json.dumps({"key": "indoor_temperature", "content": {"value": room_temperature}}))
        self.redis_instance.setex("air-latest-temperature", 300, room_temperature)


def main():
    item = DustNode()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
