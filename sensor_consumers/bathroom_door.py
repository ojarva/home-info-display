# coding=utf-8

from utils import SensorConsumerBase
import json
import sys


class Bathroom(SensorConsumerBase):

    def __init__(self):
        SensorConsumerBase.__init__(self)
        self.bathroom_door_state = None

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
        ceiling_temperature = round(data["data"]["ceiling_temperature"], 1)
        pir_triggered = data["data"]["pir"] == "1"
        door_open = data["data"]["door"] == "1"

        if self.bathroom_door_state is not None:
            if door_open != self.bathroom_door_state:
                self.redis_instance.publish("lightcontrol-triggers-pubsub", json.dumps({"key": "bathroom-door", "trigger": "switch"}))
        self.bathroom_door_state = door_open
        self.redis_instance.publish("switch-pubsub", json.dumps({"source": "bathroom-door", "name": "bathroom-door", "value": door_open}))

        if pir_triggered:
            self.redis_instance.publish("lightcontrol-triggers-pubsub", json.dumps({"key": "corridor-pir", "trigger": "pir"}))
            self.redis_instance.publish("pir-pubsub", json.dumps({"source": "bathroom-door", "name": "corridor"}))

        if bathroom_temperature < 5 or bathroom_temperature > 60:
            bathroom_temperature = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "bathroom-door", "name": "bathroom", "value": corridor_temperature}))

        if corridor_temperature < 5 or corridor_temperature > 60:
            corridor_temperature = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "bathroom-door", "name": "corridor", "value": corridor_temperature}))

        if bathroom_humidity < 5 or bathroom_humidity > 100:
            bathroom_humidity = None
        else:
            self.redis_instance.publish("humidity-pubsub", json.dumps({"source": "bathroom-door", "name": "bathroom", "value": bathroom_humidity}))

        if corridor_humidity < 5 or corridor_humidity > 100:
            corridor_humidity = None
        else:
            self.redis_instance.publish("humidity-pubsub", json.dumps({"source": "bathroom-door", "name": "corridor", "value": corridor_humidity}))

        if ceiling_temperature < 5 or ceiling_temperature > 60:
            ceiling_temperature = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "bathroom-door", "name": "corridor-ceiling", "value": ceiling_temperature}))

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
                "ceiling_temperature": ceiling_temperature,
                "pir_triggered": pir_triggered,
                "door_open": door_open,
            },
        }
        self.insert_into_influx([influx_data])


def main():
    item = Bathroom()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
