# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
import redis
import datetime
import sys

class Dishwasher(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "appliances")
        self.on_since = None
        self.running_time = None
        self.off_since = None
        self.show_was_running = False

    def run(self):
        self.subscribe("dishwasher-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        if "action" in data:
            if data["action"] == "user_dismissed":
                # User dismissed the dialog - reset the state
                self.off_since = None
                self.show_was_running = False
                self.delete_notification("dishwasher")
            return

        self.insert_into_influx([{
            "measurement": "dishwasher",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "power_consumption": round(data["data"]["power_consumption"], 3),
            }
        }])
        if data["data"]["power_consumption"] < 0.05:
            if not self.off_since:
                self.off_since = datetime.datetime.now()

            if (datetime.datetime.now() - self.off_since) > datetime.timedelta(minutes=3) and self.show_was_running:
                if self.on_since:
                    self.running_time = datetime.datetime.now() - self.on_since
                    if self.running_time < datetime.timedelta(minutes=30):
                        print "Dishwasher didn't run long enough: %s" % self.running_time
                    elif self.running_time > datetime.timedelta(minutes=120):
                        print "Ran too long time: %s" % self.running_time
                if self.running_time:
                    message = "Pesukone valmis ({from_now_timestamp}, päällä %s)" % self.format_elapsed_time(self.running_time)
                else:
                    message = "Pesukone valmis ({from_now_timestamp})"
                self.update_notification("dishwasher", message, True, from_now_timestamp=self.off_since)

                self.on_since = None

        if data["data"]["power_consumption"] > 0.4:
            if not self.on_since:
                self.on_since = datetime.datetime.now()
            self.off_since = None

        if self.on_since:
            self.show_was_running = True
            self.update_notification("dishwasher", "Pesukone päällä ({elapsed_since})", False, elapsed_since=self.on_since)


def main():
    item = Dishwasher()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
