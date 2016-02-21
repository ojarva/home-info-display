# coding=utf-8

from utils import SensorConsumerBase
import datetime
import sys


class MicrowaveState(object):

    def __init__(self):
        self.stuff_inside = False
        self.stuff_inside_since = None
        self.stuff_inside_alarmed = False
        self.last_used_at = None
        self.on_since = None
        self.total_time_running = datetime.timedelta(0)

        self.door_open = False
        self.running = False
        self.light_on = False

    def print_state(self):
        print "door_open=%s, running=%s, light_on=%s, stuff_inside=%s, last_used_at=%s, on_since=%s, total_time_running=%s" % (self.door_open, self.running, self.light_on, self.stuff_inside, self.last_used_at, self.on_since, self.total_time_running)

    def set_door_open(self):
        self.set_stopped()
        self.door_open = True
        self.stuff_inside = False
        self.stuff_inside_since = None

    def set_door_closed(self):
        self.door_open = False

    def set_running(self):
        if not self.running:
            self.stuff_inside = True
            self.stuff_inside_alarmed = False
            self.on_since = datetime.datetime.now()
        self.stuff_inside_since = datetime.datetime.now()
        self.set_light_on()
        self.running = True

    def set_stopped(self):
        if self.running:
            self.last_used_at = datetime.datetime.now()
            if self.on_since:
                self.total_time_running += (datetime.datetime.now() - self.on_since)
            self.on_since = None
        self.running = False

    def set_light_on(self):
        if not self.light_on:
            self.total_time_running = datetime.timedelta(0)
        self.light_on = True

    def set_light_off(self):
        self.light_on = False

    def get_total_time_running(self):
        if self.on_since:
            return self.total_time_running + (datetime.datetime.now() - self.on_since)
        return self.total_time_running

    def get_total_time_running_formatted(self):
        """ Get MM:SS formatted total time """
        total_running_time = self.get_total_time_running()
        seconds = total_running_time.total_seconds()
        minutes = int(seconds / 60)
        seconds = int(seconds - (minutes * 60))
        return str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

    def get_calculated_on_since(self):
        """ Returns timestamp where (now - timestamp) matches to total running time """
        total_running_time = self.get_total_time_running()
        return datetime.datetime.now() - total_running_time


class Microwave(SensorConsumerBase):
    def __init__(self):
        SensorConsumerBase.__init__(self, "home")
        self.state = MicrowaveState()
        self.delete_notification("microwave")

    def run(self):
        self.subscribe("microwave-pubsub", self.pubsub_callback)

    def pubsub_callback(self, data):
        self.state.print_state()

        if "action" in data:
            if data["action"] == "user_dismissed":
                self.state.stuff_inside = False
                self.delete_notification("microwave")
            return

        power_consumption = round(data["data"]["power_consumption"], 3)
        if 0 > power_consumption or power_consumption > 3000:
            print "Invalid power consumption for microwave: %s. Setting to null." % power_consumption
            power_consumption = None

        door_open = int(data["data"]["door"]) == 1
        self.insert_into_influx([{
            "measurement": "microwave",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "tags": {
                "location": "kitchen",
            },
            "fields": {
                "power_consumption": power_consumption,
                "door": door_open,
            }
        }])

        if door_open:
            self.state.set_door_open()

            if data["data"]["power_consumption"] > 0.08:
                self.state.set_light_on()
                # Door is open, microwave is not running but still consumes energy -> timer is not set to zero.
                if self.state.get_total_time_running() > datetime.timedelta(seconds=2):
                    message = "Mikron valo päällä (%s)" % self.state.get_total_time_running_formatted()
                else:
                    message = "Mikron valo päällä"
            else:
                self.state.set_light_off()
                if self.state.get_total_time_running() > datetime.timedelta(seconds=2):
                    message = "Mikron ovi auki (%s)" % self.state.get_total_time_running_formatted()
                else:
                    message = "Mikron ovi auki"

            self.update_notification("microwave", message, False)
            return
        else:
            self.state.set_door_closed()
            if data["data"]["power_consumption"] > 0.2:
                self.state.set_running()
                self.update_notification("microwave", "Mikro päällä ({elapsed_since})", False, elapsed_since=self.state.get_calculated_on_since())
                return
            else:
                self.state.set_stopped()
                if self.state.stuff_inside and self.state.get_total_time_running() > datetime.timedelta(seconds=2):
                    self.update_notification("microwave", "Mikrossa kamaa (%s, {from_now_timestamp})" % self.state.get_total_time_running_formatted(), True, from_now_timestamp=self.state.last_used_at)
                    if not self.state.stuff_inside_alarmed and self.state.stuff_inside_since and datetime.datetime.now() - self.state.stuff_inside_since > datetime.timedelta(seconds=60):
                        self.play_sound("normal")
                        self.state.stuff_inside_alarmed = True
                else:
                    self.delete_notification("microwave")


def main():
    item = Microwave()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
