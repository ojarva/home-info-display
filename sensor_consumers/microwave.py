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

class Microwave(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.on_since = None
        self.door_opened_after_use = True
        self.light_on_set = False
        self.last_used_at = None

    def run(self):
        self.subscribe("microwave-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            if data["action"] == "user_dismissed":
                self.door_opened_after_use = True
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
            self.on_since = None

            if data["data"]["power_consumption"] > 0.08 and not self.light_on_set:
                # Door is open, microwave is not running but still consumes energy -> timer is not set to zero.
                self.update_notification("microwave", "Mikron valo päällä", True)
                self.light_on_set = True
            else:
                self.delete_notification("microwave")
            self.door_opened_after_use = True
            return
        if data["data"]["power_consumption"] > 0.2:
            if not self.on_since:
                self.on_since = datetime.datetime.now()
            self.update_notification("microwave", "Mikro päällä ({elapsed_since})", False, elapsed_since=self.on_since)
            self.last_used_at = datetime.datetime.now()
            self.door_opened_after_use = False
            self.light_on_set = False
            return

        # Not running, but door is not open either
        self.on_since = None

        # If microwave has been used, but door has not been opened, there should be something inside.
        if self.last_used_at and not self.door_opened_after_use:
            self.update_notification("microwave", "Mikrossa kamaa ({from_now_timestamp})", True, from_now_timestamp=self.last_used_at)

def main():
    item = Microwave()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
