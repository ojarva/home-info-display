# coding=utf-8

from utils import SensorConsumerBase
from dishwasher_parser import DishwasherParser
import datetime
import json
import redis
import requests.exceptions
import sys
import time


class Dishwasher(SensorConsumerBase):

    PHASE_MAPPING = {
        "starting": "alkaa",
        "prewash": "esipesu",
        "washing-1": "1. pesu",
        "mid-washing": "välihuuhtelu",
        "washing-2": "huuhtelu",
        "finishing": "lopettaa",
        "cooling": "jäähdytys"
    }

    def __init__(self):
        SensorConsumerBase.__init__(self, "home")
        self.running_dialog_visible = False
        self.finished_dialog_visible = False
        self.dishwasher_parser = DishwasherParser()
        self.redis = redis.StrictRedis()
        state = self.redis.get("dishwasher-parser-state")
        if state:
            state = json.loads(state)
            print "Restoring state from redis"
            self.dishwasher_parser.load_state(state)
        try:
            self.delete_notification("dishwasher")
        except requests.exceptions.ConnectionError as err:
            print "Initial deleting of notifications failed. Sleep 10s before exiting."
            time.sleep(10)
            raise err

    def run(self):
        self.subscribe("dishwasher-pubsub", self.pubsub_callback)

    @classmethod
    def _determine_program(cls, program_data):
        if program_data is None:
            return
        if len(program_data) == 2 and "50C" in program_data and "65C" in program_data:
            return "50/65C"
        if len(program_data) == 1:
            if "quick" in program_data:
                return "pika"
            if "prewash" in program_data:
                return "esipesu"
        return "?"

    def pubsub_callback(self, data):
        if "action" in data:
            if data["action"] == "user_dismissed":
                # User dismissed the dialog
                self.running_dialog_visible = False
            return

        power_consumption = round(data["data"]["power_consumption"], 3) * 230
        if 0 > power_consumption or power_consumption > 3000:
            print "Invalid power consumption for dishwasher: %s. Setting to null." % power_consumption
            power_consumption = None

        self.insert_into_influx([{
            "measurement": "dishwasher",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "tags": {
                "location": "kitchen",
            },
            "fields": {
                "power_consumption": power_consumption,
            },
        }])

        parser_data = self.dishwasher_parser.add_value(datetime.datetime.now(), data["data"]["power_consumption"] * 230)
        self.redis.setex("dishwasher-parser-state", 120, json.dumps(self.dishwasher_parser.get_state()))

        if parser_data:
            if parser_data["current_phase"] is None:
                pass
            elif parser_data["current_phase"] == "finished":
                program = self._determine_program(parser_data["current_program"])
                message = "Pesukone valmis ({from_now_timestamp}, päällä %s, %s)" % (self.format_timedelta(parser_data["duration"]), program)
                self.running_dialog_visible = False
                self.finished_dialog_visible = True
                self.update_notification("dishwasher", message, True, from_now_timestamp=datetime.datetime.now())
                self.play_sound("finished")
            elif parser_data.get("exc") == "noise_or_interrupted":
                print "Noise or interrupted run - remove incorrect dialog (if exists)"
                if self.running_dialog_visible:
                    self.delete_notification("dishwasher")
                    self.running_dialog_visible = False
                    self.finished_dialog_visible = True
            else:
                program = self._determine_program(parser_data["current_program"])
                message = "Astiat: "
                components = []
                if "eta" in parser_data and parser_data["eta"] is not None:
                    eta = datetime.datetime.now() + parser_data["eta"]
                    eta = eta.strftime("%H:%M:%S")
                    components.append("ETA klo %s" % eta)
                if program:
                    components.append(program)
                if parser_data["current_phase"]:
                    phase_translated = self.PHASE_MAPPING[parser_data["current_phase"]]
                    components.append(phase_translated)
                if len(components) == 0:
                    components.append("{elapsed_since}")
                message = message + ", ".join(components)
                self.running_dialog_visible = True
                self.finished_dialog_visible = False
                self.update_notification("dishwasher", message, False, elapsed_since=parser_data["running_since"])


def main():
    item = Dishwasher()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
