# coding=utf-8

from setproctitle import setproctitle
from utils import SensorConsumerBase
import datetime
import os
import sys
import json


class FridgeInside(SensorConsumerBase):
    THRESHOLD_CONFIG = {
        "fridge_temperature2": {
            "notification": "fridge-temperature",
            "message": "Jääkaappi liian lämmin: {value}&deg;C ({{elapsed_since}})",
            "normal": {
                "gt": 7,
                "sound": datetime.timedelta(minutes=30),
                "delay": datetime.timedelta(seconds=30),
                "escalate": datetime.timedelta(minutes=31),
            },
            "high": {
                "gt": 10,
                "sound": datetime.timedelta(minutes=15),
                "escalate": datetime.timedelta(minutes=30),
            },
            "urgent": {
                "gt": 15,
                "sound": datetime.timedelta(minutes=3),
            },
        },
        "freezer_temperature1": {
            "notification": "small-freezer-temperature",
            "message": "Pikkupakastin liian lämmin: {value}&deg;C ({{elapsed_since}})",
            "normal": {
                "gt": -20,
                "sound": datetime.timedelta(minutes=30),
                "delay": datetime.timedelta(seconds=30),
                "escalate": datetime.timedelta(minutes=15),
            },
            "high": {
                "gt": -15,
                "sound": datetime.timedelta(minutes=15),
                "escalate": datetime.timedelta(minutes=60),
            },
            "urgent": {
                "gt": -10,
                "sound": datetime.timedelta(minutes=3),
            },
        },
        "fridge_door_open": {
            "notification": "fridge-door-open",
            "message": "Jääkaapin ovi auki ({{elapsed_since}})",
            "normal": {
                "bool": True,
                "sound": datetime.timedelta(seconds=30),
                "escalate": datetime.timedelta(seconds=60),
            },
            "high": {
                "sound": datetime.timedelta(seconds=0),
                "escalate": datetime.timedelta(minutes=10),
            },
            "urgent": {
                "sound": datetime.timedelta(seconds=0),
            }
        },
        "freezer_door_open": {
            "message": "Pikkupakastimen ovi auki ({{elapsed_since}})",
            "notification": "small-freezer-door-open",
            "normal": {
                "bool": True,
                "sound": datetime.timedelta(seconds=30),
                "escalate": datetime.timedelta(seconds=60),
            },
            "high": {
                "sound": datetime.timedelta(seconds=0),
                "escalate": datetime.timedelta(minutes=5),
            },
            "urgent": {
                "sound": datetime.timedelta(seconds=0),
            }
        },
    }

    def __init__(self, redis_host, redis_port):
        SensorConsumerBase.__init__(self, redis_host=redis_host, redis_port=redis_port)
        self.initialize_notifications(self.THRESHOLD_CONFIG)

    def run(self):
        self.subscribe("fridge-inside-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        print("Received %s" % data)
        if "action" in data:
            if data["action"] == "user_dismissed":
                pass
            return

        if data["data"]["freezer_temperature1"] < -35 or data["data"]["freezer_temperature1"] > 30:
            data["data"]["freezer_temperature1"] = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "fridge", "name": "freezer", "value": data["data"]["freezer_temperature1"]}))

        if data["data"]["fridge_temperature1"] < -35 or data["data"]["fridge_temperature1"] > 30:
            data["data"]["fridge_temperature1"] = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "fridge", "name": "fridge-upper", "value": data["data"]["fridge_temperature1"]}))

        if data["data"]["fridge_temperature2"] < -35 or data["data"]["fridge_temperature2"] > 30:
            data["data"]["fridge_temperature2"] = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "fridge", "name": "fridge-middle", "value": data["data"]["fridge_temperature2"]}))

        if data["data"]["fridge_temperature3"] < -35 or data["data"]["fridge_temperature3"] > 30:
            data["data"]["fridge_temperature3"] = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "fridge", "name": "fridge-cooling-element", "value": data["data"]["fridge_temperature3"]}))

        if data["data"]["fridge_temperature4"] < -35 or data["data"]["fridge_temperature4"] > 30:
            data["data"]["fridge_temperature4"] = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "fridge", "name": "fridge-middle-rh-sensor", "value": data["data"]["fridge_temperature4"]}))

        if data["data"]["fridge_humidity"] < 0 or data["data"]["fridge_humidity"] > 100:
            data["data"]["fridge_humidity"] = None
        else:
            self.redis_instance.publish("humidity-pubsub", json.dumps({"source": "fridge", "name": "fridge-middle-rh-sensor", "value": data["data"]["fridge_humidity"]}))

        self.redis_instance.publish("switch-pubsub", json.dumps({"source": "fridge", "name": "fridge-door", "value": data["data"]["fridge_door_open"]}))
        self.redis_instance.publish("switch-pubsub", json.dumps({"source": "fridge", "name": "freezer-door", "value": data["data"]["freezer_door_open"]}))

        self.insert_into_influx([{
            "measurement": "fridge",
            "tags": {
                "unit": "inside",
                "location": "kitchen",
            },
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": data["data"],
        }])

        self.check_notifications(data["data"])


def main():
    setproctitle("fridge-inside: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    item = FridgeInside(redis_host, redis_port)
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
