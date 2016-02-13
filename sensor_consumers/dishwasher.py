# coding=utf-8

from local_settings import *
from utils import SensorConsumerBase
from dishwasher_parser import DishwasherParser
import datetime
import sys

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
        SensorConsumerBase.__init__(self, "indoor_air_quality")
        self.show_was_running = False
        self.dishwasher_parser = DishwasherParser()

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
                pass
            return

        self.insert_into_influx([{
            "measurement": "dishwasher",
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {
                "power_consumption": round(data["data"]["power_consumption"], 3),
            }
        }])

        parser_data = self.dishwasher_parser.add_value(datetime.datetime.now(), data["data"]["power_consumption"] * 230)

        if parser_data:
            if parser_data["current_phase"] is None:
                pass
            elif parser_data["current_phase"] == "finished":
                program = self._determine_program(parser_data["current_program"])
                message = "Pesukone valmis ({from_now_timestamp}, päällä %s, %s)" % (parser_data["duration"], program)
                self.update_notification("dishwasher", message, True, from_now_timestamp=datetime.datetime.now())
                self.play_sound("finished")
            else:
                program = self._determine_program(parser_data["current_program"])
                message = "Astiat: "
                components = []
                if "eta" in parser_data and parser_data["eta"] is not None:
                    eta = datetime.datetime.now() + parser_data["eta"]
                    eta = eta.strftime("%H:%M:%S")
                    components.append("ETA %s" % eta)
                if program:
                    components.append(program)
                if parser_data["current_phase"]:
                    phase_translated = self.PHASE_MAPPING[parser_data["current_phase"]]
                    components.append(phase_translated)
                if len(components) == 0:
                    components.append("{elapsed_since}")
                message = message + ", ".join(components)
                self.update_notification("dishwasher", message, False, elapsed_since=parser_data["running_since"])


def main():
    item = Dishwasher()
    item.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
