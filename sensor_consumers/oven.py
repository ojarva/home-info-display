# coding=utf-8

from setproctitle import setproctitle
from utils import SensorConsumerBase
import datetime
import os
import sys


class Oven(SensorConsumerBase):

    def __init__(self, redis_host, redis_port):
        SensorConsumerBase.__init__(self, redis_host=redis_host, redis_port=redis_port)
        self.notification_visible = False

    def run(self):
        self.subscribe("oven-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return
        temperature = round(data["data"]["oven_temperature"], 1)
        room_temperature = round(data["data"]["room_temperature"], 1)
        outside_box_room_temperature = round(data["data"]["outside_box_temperature"], 1)
        if 0 > temperature or temperature > 400:
            print("Invalid value for oven temperature: %s. Setting to null" % temperature)
            temperature = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "oven", "name": "inside", "value": temperature}))

        if 0 > room_temperature or room_temperature > 40:
            print("Invalid value for room temperature (sensor calibration): %s. Setting to null." % room_temperature)
            room_temperature = None
        if 0 > outside_box_room_temperature or outside_box_room_temperature > 40:
            print("Invalid value for room temperature (outside of the box): %s. Setting to null." % outside_box_room_temperature)
            outside_box_room_temperature = None
        else:
            self.redis_instance.publish("temperature-pubsub", json.dumps({"source": "oven", "name": "floor", "value": outside_box_room_temperature}))

        self.insert_into_influx([{
            "measurement": "oven",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "tags": {
                "location": "kitchen",
            },
            "fields": {
                "oven_temperature": temperature,
                "box_temperature": room_temperature,
                "kitchen_floor_temperature": outside_box_room_temperature,
            }
        }])
        if temperature is None:
            self.update_notification("oven", "Uunin lämpötila ei ole saatavilla.", False)
        elif temperature > 50:
            self.update_notification("oven", "Uuni: %s&deg;C" % int(round(temperature)), False)
            self.notification_visible = True
        elif self.notification_visible:
            self.delete_notification("oven")
            self.notification_visible = False


def main():
    setproctitle("oven: run")
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    item = Oven(redis_host, redis_port)
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
