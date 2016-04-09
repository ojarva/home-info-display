# coding=utf-8

from utils import SensorConsumerBase
import sys
import datetime
import json


class Door(SensorConsumerBase):

    def __init__(self):
        SensorConsumerBase.__init__(self)
        self.notification = None
        self.delete_notification("door")
        self.door_open_elapsed_since = None

        self.outer_door_state = None
        self.inner_door_state = None

    def run(self):
        self.subscribe("door-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return

        influx_data = {
            "measurement": "door",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "tags": {
                "location": "door",
            },
            "fields": data["data"],
        }
        self.insert_into_influx([influx_data])

        if self.outer_door_state is not None:
            if self.outer_door_state != data["data"]["door_outer_open"]:
                self.redis_instance.publish("lightcontrol-triggers-pubsub", json.dumps({"key": "outer-door", "trigger": "switch", "open": data["data"]["door_outer_open"]}))
        if self.inner_door_state is not None:
            if self.inner_door_state != data["data"]["door_inner_open"]:
                self.redis_instance.publish("lightcontrol-triggers-pubsub", json.dumps({"key": "inner-door", "trigger": "switch", "open": data["data"]["door_inner_open"]}))

        self.outer_door_state = data["data"]["door_outer_open"]
        self.inner_door_state = data["data"]["door_inner_open"]

        if data["data"]["door_outer_open"]:
            if not self.door_open_elapsed_since:
                self.door_open_elapsed_since = datetime.datetime.now()
            notification = {
                "notification": "door",
                "message": "Ulko-ovi on auki ({elapsed_since})",
                "user_dismissable": False,
                "elapsed_since": self.door_open_elapsed_since,
            }
            if self.notification != notification:
                self.notification = notification
                self.update_notification_from_dict(**notification)
        else:
            if self.door_open_elapsed_since:
                self.delete_notification("door")
                self.door_open_elapsed_since = None
                self.notification = None


def main():
    item = Door()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
