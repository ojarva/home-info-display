# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class Microwave(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self)
        self.on_since = None
        self.door_opened_after_use = True
        self.last_used_at = None

    def run(self):
        self.subscribe("microwave-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        door_open = int(data["data"]["door"]) == 1
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
            self.update_notification("microwave", "Mikro päällä (%s)" % self.get_elapsed_time(self.on_since), False)
            return

        # Not running, but door is not open either
        self.door_opened_after_use = False
        self.on_since = None
        if not self.last_used_at:
            self.last_used_at = datetime.datetime.now()
        self.update_notification("microwave", "Mikrossa kamaa (%s)" % self.get_elapsed_time(self.last_used_at), True)

def main():
    item = Microwave()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
