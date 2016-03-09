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
    DATA_CONFIG = {
        "update-interval": {
            "message": "Pakastimelta ei tule tietoja ({{elapsed_since}})",
            "notification": "freezer-data-update",
            "normal": {
                "delay": datetime.timedelta(seconds=45),
                "sound": datetime.timedelta(minutes=5),
                "escalate": datetime.timedelta(minutes=10)
            },
            "high": {
                "delay": datetime.timedelta(seconds=45),
                "sound": datetime.timedelta(minutes=60),
                "escalate": datetime.timedelta(minutes=10)
            }
        }
    }

    def __init__(self):
        SensorConsumerBase.__init__(self)
        self.initialize_notifications(self.THRESHOLD_CONFIG)

    def run(self):
        self.subscribe("freezer-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        door_open = int(data["data"]["door"]) == 0
        power_consumption = round(data["data"]["power_consumption"] * 230, 2)
        if 0 > power_consumption or power_consumption > 3000:
            print "Invalid power consumption for freezer: %s. Setting to null." % (power_consumption)
            power_consumption = None
        temperature1 = round(data["data"]["temperature1"], 1)
        temperature2 = round(data["data"]["temperature2"], 1)
        if -35 > temperature1 or temperature1 > 40:
            print "Invalid value for temperature1: %s. Setting to null." % temperature1
            temperature1 = None
        if -35 > temperature2 or temperature2 > 40:
            print "Invalid value for temperature2: %s. Setting to null." % temperature2
            temperature2 = None

        processed_data = {
            "power_consumption": power_consumption,
            "door": door_open,
            "temperature1": temperature1,
            "temperature2": temperature2,
            "water": data["data"]["water"],
        }

        self.insert_into_influx([{
            "measurement": "freezer",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "tags": {
                "location": "kitchen",
            },
            "fields": processed_data,
        }])

        self.check_notifications(processed_data)


def main():
    item = Freezer()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
