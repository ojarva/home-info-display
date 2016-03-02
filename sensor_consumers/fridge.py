# coding=utf-8

from utils import SensorConsumerBase
import datetime
import sys


class Fridge(SensorConsumerBase):

    def __init__(self):
        SensorConsumerBase.__init__(self, "home")

    def run(self):
        self.subscribe("fridgetop-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        kitchen_ceiling_temperature = round(
            data["data"]["room_temperature"], 1)
        if kitchen_ceiling_temperature < 10 or kitchen_ceiling_temperature > 40:
            print "Invalid temperature for kitchen ceiling sensor: %s. Setting to null." % kitchen_ceiling_temperature
            kitchen_ceiling_temperature = None
        power_consumption = round(data["data"]["power_consumption"] * 230, 2)
        if 0 > power_consumption or power_consumption > 3000:
            print "Invalid power consumption for fridge: %s. Setting to null." % power_consumption
            power_consumption = None

        self.insert_into_influx([{
            "measurement": "fridge",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "tags": {
                "unit": "consumption-meter",
                "location": "kitchen",
            },
            "fields": {
                "power_consumption": power_consumption,
                "kitchen_ceiling_temperature": kitchen_ceiling_temperature,
            },
        }])


def main():
    item = Fridge()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
