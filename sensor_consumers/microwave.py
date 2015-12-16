# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

"""
- ~34W -> light on
- ~1W -> off
- >120W -> running
"""

class MicrowaveState:

    def __init__(self):
        self.stuff_inside = False
        self.last_used_at = None
        self.on_since = None

    def off(self):
        self.on_since = None

    def on(self):
        if not self.on_since:
            self.on_since = datetime.datetime.now()
        self.last_used_at = datetime.datetime.now()
        self.stuff_inside = True

    def door_opened(self):
        self.stuff_inside = False

class Microwave(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.state = MicrowaveState()
        self.delete_notification("microwave")

    def run(self):
        self.subscribe("microwave-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            if data["action"] == "user_dismissed":
                self.state.stuff_inside = False
                self.delete_notification("microwave")
            return

        door_open = int(data["data"]["door"]) == 1
        self.insert_into_influx([{
            "measurement": "microwave",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "power_consumption": round(data["data"]["power_consumption"], 3),
                "door": door_open,
            }
        }])

        if door_open:
            print "Door is open"

            # Must be off, since the door is open
            self.state.off()
            self.state.door_opened()

            if data["data"]["power_consumption"] > 0.08:
                # Door is open, microwave is not running but still consumes energy -> timer is not set to zero.
                self.update_notification("microwave", "Mikron valo päällä", False)
            else:
                self.delete_notification("microwave")
            return
        elif data["data"]["power_consumption"] > 0.2:
            self.state.on()
            self.update_notification("microwave", "Mikro päällä ({elapsed_since})", False, elapsed_since=self.state.on_since)
            return
        else:
            # Not running and door is not open either
            self.state.off()

            # If microwave has been used, but door has not been opened, there should be something inside.
            if self.state.stuff_inside:
                self.update_notification("microwave", "Mikrossa kamaa ({from_now_timestamp})", True, from_now_timestamp=self.state.last_used_at)

def main():
    item = Microwave()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
