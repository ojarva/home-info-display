# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class FridgeInside(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.delete_notification("fridge-door-open")
        self.delete_notification("fridge-temperature")
        self.delete_notification("small-freezer-door-open")
        self.delete_notification("small-freezer-temperature")

        self.fridge_temperature_too_high_since = None
        self.freezer_temperature_too_high_since = None

        self.fridge_door_open_since = None
        self.freezer_door_open_since = None

    def run(self):
        self.subscribe("fridge-inside-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        print "Received %s" % data
        if "action" in data:
            if data["action"] == "user_dismissed":
                self.delete_notification("microwave")
            return

        self.insert_into_influx([{
            "measurement": "fridge-inside",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": data["data"],
        }])

        temperature = data["data"]["fridge_temperature2"]
        if temperature > 10:
            if self.fridge_temperature_too_high_since is None:
                self.fridge_temperature_too_high_since = datetime.datetime.now()
            level = "normal"
            if datetime.datetime.now() - self.fridge_temperature_too_high_since > datetime.timedelta(minutes=30):
                level = "high"
            self.update_notification("fridge-temperature", "Jääkaappi liian lämmin: %s ({elapsed_since})" % temperature, False, elapsed_since=self.fridge_temperature_too_high_since, level=level)
        else:
            self.fridge_temperature_too_high_since = None

        temperature = data["data"]["freezer_temperature1"]
        if temperature > 10:
            if self.freezer_temperature_too_high_since is None:
                self.freezer_temperature_too_high_since = datetime.datetime.now()
                level = "normal"
            if datetime.datetime.now() - self.freezer_temperature_too_high_since > datetime.timedelta(minutes=30):
                level = "high"
            self.update_notification("small-freezer-temperature", "Pikkupakastin liian lämmin: %s ({elapsed_since})" % temperature, False, elapsed_since=self.freezer_temperature_too_high_since, level=level)
        else:
            self.freezer_temperature_too_high_since = None


        if data["data"]["fridge_door_open"]:
            if not self.fridge_door_open_since:
                self.fridge_door_open_since = datetime.datetime.now()
            level = "normal"
            if datetime.datetime.now() - self.fridge_door_open_since > datetime.timedelta(seconds=15):
                level = "high"
            self.update_notification("fridge-door-open", "Jääkaapin ovi auki ({from_now_timestamp})", False, from_now_timestamp=self.fridge_door_open_since, level=level)
        else:
            self.delete_notification("fridge-door-open")
            self.fridge_door_open_since = None

        if data["data"]["freezer_door_open"]:
            if not self.freezer_door_open_since:
                self.freezer_door_open_since = datetime.datetime.now()
            level = "normal"
            if datetime.datetime.now() - self.freezer_door_open_since > datetime.timedelta(seconds=15):
                level = "high"
            self.update_notification("small-freezer-door-open", "Pikkupakastimen ovi auki ({from_now_timestamp})", False, from_now_timestamp=self.freezer_door_open_since, level=level)
        else:
            self.delete_notification("small-freezer-door-open")
            self.freezer_door_open_since = None

def main():
    item = FridgeInside()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
