# coding=utf-8

from utils import SensorConsumerBase
import datetime
import sys


class Freezer(SensorConsumerBase):
    THRESHOLD_CONFIG = {
        "temperature1": {
            "notification": "freezer-temperature",
            "message": "Pakastin on liian lämmin: {value}&deg;C ({{elapsed_since}})",
            "normal": {
                "gt": -17.5,
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
        "door_open": {
            "message": "Pakastimen ovi auki ({{elapsed_since}})",
            "notification": "freezer-door-open",
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
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.initialize_notifications(self.THRESHOLD_CONFIG)

    def run(self):
        self.subscribe("freezer-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        door_open = int(data["data"]["door"]) == 0

        processed_data = {
            "power_consumption": round(data["data"]["power_consumption"], 3),
            "door": door_open,
            "temperature1": round(data["data"]["temperature1"], 1),
            "temperature2": round(data["data"]["temperature2"], 1),
            "water": data["data"]["water"],
        }

        self.insert_into_influx([{
            "measurement": "freezer",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": processed_data,
        }])

        self.check_notifications(processed_data)


def main():
    item = Freezer()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
