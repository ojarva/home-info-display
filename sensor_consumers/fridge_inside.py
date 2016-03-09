# coding=utf-8

from utils import SensorConsumerBase
import datetime
import sys


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

    def __init__(self):
        SensorConsumerBase.__init__(self)
        self.initialize_notifications(self.THRESHOLD_CONFIG)

    def run(self):
        self.subscribe("fridge-inside-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        print "Received %s" % data
        if "action" in data:
            if data["action"] == "user_dismissed":
                pass
            return

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
    item = FridgeInside()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
