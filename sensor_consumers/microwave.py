# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class Microwave(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "appliances")
        self.on_since = None
        self.door_opened_after_use = True
        self.last_used_at = None

    def run(self):
        self.subscribe("microwave-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            return
        door_open = int(data["data"]["door"]) == 1
        self.insert_into_influx([{
            "measurement": "microwave",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "power_consumption": round(data["data"]["power_consumption"], 3),
            }
            }])
        if door_open:
            # Must be off, as the door is open
            print "Door is open"
            self.delete_notification("microwave")
            self.door_opened_after_use = True
            self.on_since = None
            return
        if data["data"]["power_consumption"] > 1:
            if not self.on_since:
                self.on_since = datetime.datetime.now()
            self.update_notification("microwave", "Mikro päällä ({elapsed_since})", False, elapsed_since=self.on_since)
            self.last_used_at = datetime.datetime.now()
            self.door_opened_after_use = False
            return

        # Not running, but door is not open either
        self.on_since = None
        if self.last_used_at and not self.door_opened_after_use:
            self.update_notification("microwave", "Mikrossa kamaa ({from_now_timestamp})", True, from_now_timestamp=self.last_used_at)

def main():
    item = Microwave()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
