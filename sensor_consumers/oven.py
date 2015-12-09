# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys
import math

class Oven(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self)

    def run(self):
        self.subscribe("oven-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return
        temperature = data["data"]["oven_temperature"]
        if temperature > 50:
            self.update_notification("oven", "Uuni: %s&deg;C" % math.round(temperature), False)
        else:
            self.delete_notification("oven")

def main():
    item = Oven()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
