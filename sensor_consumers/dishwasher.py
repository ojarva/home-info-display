# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class Dishwasher(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self)
        self.on_since = None
        self.running_time = None
        self.off_since = None

    def run(self):
        self.subscribe("dishwasher-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if data["data"]["power_consumption"] < 0.05:
            if self.off_since:
                if (datetime.datetime.now() - self.off_since) > datetime.timedelta(minutes=3):
                    if self.on_since:
                        self.running_time = datetime.datetime.now() - self.on_since
                        if self.running_time < datetime.timedelta(minutes=30):
                            print "Dishwasher didn't run long enough: %s" % self.running_time
                        elif self.running_time > datetime.timedelta(minutes=120):
                            print "Ran too long time: %s" % self.running_time
                    if self.running_time:
                        message = "Pesukone valmis (%s, päällä %s)" % (self.get_elapsed_time(self.off_since), self.format_elapsed_time(self.running_time))
                    else:
                        message = "Pesukone valmis (%s)" % self.get_elapsed_time(self.off_since)
                    self.update_notification("dishwasher", message, True)

                    self.on_since = None
            else:
                self.off_since = datetime.datetime.now()

        if data["data"]["power_consumption"] > 2:
            if not self.on_since:
                self.on_since = datetime.datetime.now()

        if data["data"]["power_consumption"] > 0.5:
            self.off_since = None

        if self.on_since:
            self.update_notification("dishwasher", "Pesukone päällä (%s)" % self.get_elapsed_time(self.on_since), False)


def main():
    item = Dishwasher()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
