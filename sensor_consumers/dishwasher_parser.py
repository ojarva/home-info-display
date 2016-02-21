import copy
import datetime
import glob
import json
import os
import sys


class DishwasherParser(object):
    STATE_TRANSITIONS = {
        "starting": ["prewash", "washing-1"],
        "prewash": ["finishing", "finished", "washing-1"],
        "washing-1": ["mid-washing"],
        "mid-washing": ["washing-2"],
        "washing-2": ["finishing", "cooling", "finished"],
        "finishing": ["cooling", "finished"],
        "cooling": ["finished"],
    }

    AVERAGE_PROGRAMS = {
        "quick": [
            ("starting", datetime.timedelta(minutes=1, seconds=36)),
            ("prewash", datetime.timedelta(minutes=1, seconds=26)),
            ("washing-1", datetime.timedelta(minutes=11, seconds=45)),
            ("mid-washing", datetime.timedelta(minutes=11, seconds=13)),
            ("washing-2", datetime.timedelta(minutes=11, seconds=20)),
            ("finishing", datetime.timedelta(minutes=5, seconds=7))
        ],
        "50C": [
            ("starting", datetime.timedelta(minutes=1, seconds=30)),
            ("prewash", datetime.timedelta(minutes=13)),
            ("washing-1", datetime.timedelta(minutes=13, seconds=51)),
            ("mid-washing", datetime.timedelta(minutes=22, seconds=18)),
            ("washing-2", datetime.timedelta(minutes=18, seconds=20)),
            ("finishing", datetime.timedelta(minutes=4, seconds=45)),
            ("cooling", datetime.timedelta(minutes=21, seconds=8))
        ],
        "65C": [
            ("starting", datetime.timedelta(seconds=5)),
            ("prewash", datetime.timedelta(minutes=14, seconds=19)),
            ("washing-1", datetime.timedelta(minutes=14, seconds=46)),
            ("mid-washing", datetime.timedelta(minutes=20, seconds=23)),
            ("washing-2", datetime.timedelta(minutes=15, seconds=04)),
            ("finishing", datetime.timedelta(minutes=5, seconds=00)),
            ("cooling", datetime.timedelta(minutes=21, seconds=8))
        ],
        "prewash": [
            ("starting", datetime.timedelta(minutes=1, seconds=18)),
            ("prewash", datetime.timedelta(minutes=13)),
        ],
    }

    ARGS = ("running_since", "last_prewash_exceeded", "first_prewash_exceeded", "last_washing_exceeded", "first_washing_exceeded", "last_noise_exceeded", "first_noise_exceeded", "phases", "current_phase", "current_program", "running_or_finished_phases", "current_phase_since")

    def __init__(self, single_run_testing=False, **kwargs):
        self.reset()
        self.single_run_testing = single_run_testing  # True for throwing exception for multiple runs on a single instance
        self.start_detected = False  # Related to previous variable, True if run has started, stays True forever.
        if kwargs.get("state"):
            self.load_state(kwargs["state"])

    def load_state(self, state):
        for arg in self.ARGS:
            setattr(self, arg, state[arg])

    def get_state(self):
        state = {}
        for arg in self.ARGS:
            state[arg] = getattr(self, arg)
        return state

    def reset(self):
        self.running_since = None
        self.last_prewash_exceeded = None
        self.first_prewash_exceeded = None
        self.last_washing_exceeded = None
        self.first_washing_exceeded = None
        self.last_noise_exceeded = None
        self.first_noise_exceeded = None
        self.phases = []
        self.current_phase = None
        self.current_program = []
        self.running_or_finished_phases = []
        self.current_phase_since = None

    def set_phase(self, phase, timestamp):
        if self.current_phase == phase:
            return
        if self.current_phase is not None:
            possible_transitions = self.STATE_TRANSITIONS[self.current_phase]
            if phase not in possible_transitions:
                print "Invalid transition from %s to %s. Only %s are allowed" % (self.current_phase, phase, possible_transitions)
                raise ValueError
        self.current_phase = phase
        self.running_or_finished_phases.append(phase)
        self.current_phase_since = timestamp
        self.phases.append({"phase": phase, "timestamp": timestamp})

    def drop_program(self, program):
        try:
            self.current_program.remove(program)
        except KeyError:
            pass

    def get_eta(self, timestamp):
        def calc_eta(program, phase, current_phase_since, timestamp):
            program_phases = self.AVERAGE_PROGRAMS[program]
            started = False
            eta = datetime.timedelta(0)
            for program_phase, duration in program_phases:
                if program_phase == phase:
                    started = True
                    current_phase_remaining = duration - (timestamp - current_phase_since)
                    if current_phase_remaining > datetime.timedelta(0):
                        eta += current_phase_remaining
                    continue
                if not started:
                    continue
                eta += duration
            return eta

        if not self.current_phase:
            return
        if len(self.current_program) == 1:
            if "quick" in self.current_program:
                return calc_eta("quick", self.current_phase, self.current_phase_since, timestamp)
            if "prewash" in self.current_program:
                return calc_eta("prewash", self.current_phase, self.current_phase_since, timestamp)
        if len(self.current_program) == 2:
            if "50C" in self.current_program and "65C" in self.current_program:
                return calc_eta("50C", self.current_phase, self.current_phase_since, timestamp)

    def get_data(self, timestamp):
        if self.running_since:
            duration = timestamp - self.running_since
        else:
            duration = None
        return {
            "current_program": self.current_program,
            "current_phase": self.current_phase,
            "running_since": self.running_since,
            "duration": duration,
            "eta": self.get_eta(timestamp),
            "phases": self.phases,
        }

    def add_value(self, timestamp, value):
        data = None
        if value is None:
            return

        if value > 2:
            if self.running_since is None:
                if self.single_run_testing and self.start_detected:
                    print "Single run testing enabled but duplicate start detected"
                    assert False
                self.start_detected = True
                self.set_phase("starting", timestamp)
                self.running_since = timestamp
                self.current_program = set(["quick", "prewash", "50C", "65C"])

        if value > 1 and self.running_since:
            self.last_noise_exceeded = timestamp
            if self.first_noise_exceeded is None:
                self.first_noise_exceeded = timestamp

        if value > 25 and value < 200:
            if len(self.running_or_finished_phases) == 1:
                self.set_phase("prewash", timestamp)
            elif "washing-1" in self.running_or_finished_phases and "mid-washing" not in self.running_or_finished_phases and timestamp - self.current_phase_since > datetime.timedelta(minutes=6):
                self.set_phase("mid-washing", timestamp)
            elif "washing-2" in self.running_or_finished_phases and "finishing" not in self.running_or_finished_phases:
                self.set_phase("finishing", timestamp)
            self.last_prewash_exceeded = timestamp
            if self.first_prewash_exceeded is None:
                self.first_prewash_exceeded = timestamp

            if self.current_phase == "prewash" and timestamp - self.current_phase_since > datetime.timedelta(minutes=2, seconds=30):
                self.drop_program("quick")
        if value > 200:
            if "washing-1" not in self.running_or_finished_phases:
                self.set_phase("washing-1", timestamp)
            if "mid-washing" in self.running_or_finished_phases:
                self.set_phase("washing-2", timestamp)
            if timestamp - self.running_since < datetime.timedelta(minutes=5):
                self.drop_program("50C")
                self.drop_program("65C")
            self.drop_program("prewash")
            if timestamp - self.running_since < datetime.timedelta(minutes=2):
                self.current_program = set(["quick"])
            self.last_washing_exceeded = timestamp
            if self.first_washing_exceeded is None:
                self.first_washing_exceeded = timestamp

        if value < 1:
            # noise / not running
            if self.running_since and self.last_noise_exceeded:
                time_diff = timestamp - self.last_noise_exceeded
                if ("50C" in self.current_program or "65C" in self.current_program) and "quick" not in self.current_program and "washing-2" in self.running_or_finished_phases:
                    last_noise_exceeded_threshold = datetime.timedelta(minutes=24)
                    if time_diff > datetime.timedelta(minutes=3) and self.current_phase == "finishing":
                        self.set_phase("cooling", timestamp)
                else:
                    last_noise_exceeded_threshold = datetime.timedelta(minutes=3)
                if time_diff > last_noise_exceeded_threshold:
                    if not self.last_prewash_exceeded:
                        print "Noise or interrupted - dishwasher didn't run."
                        data = copy.deepcopy(self.get_data(timestamp))
                        self.reset()
                        data["exc"] = "noise_or_interrupted"
                    else:
                        print "Non-running period exceeded"
                        self.set_phase("finished", timestamp)
                        if "washing-2" not in self.running_or_finished_phases and "prewash" in self.running_or_finished_phases:
                            self.current_program = set(["prewash"])

                        print "running time was from %s to %s: %s - active time until %s: %s" % (self.running_since, timestamp, timestamp - self.running_since, self.last_noise_exceeded, self.last_noise_exceeded - self.running_since)
                        for i in range(0, len(self.phases)):
                            phase = self.phases[i]
                            if i < len(self.phases) - 1:
                                diff = self.phases[i + 1]["timestamp"] - phase["timestamp"]
                            else:
                                diff = None
                            phase["diff"] = diff
                            print "%s - %s" % (phase["phase"], diff)
                        print self.current_program
                        print
                        data = copy.deepcopy(self.get_data(timestamp))
                        self.reset()

        if value < 25:
            if self.first_prewash_exceeded and self.last_prewash_exceeded:
                self.first_prewash_exceeded = None

        if value < 200:
            if self.first_washing_exceeded and self.last_washing_exceeded:
                self.first_washing_exceeded = None

        if data is not None:
            return data
        return self.get_data(timestamp)


def main():
    def get_program(filename):
        d = os.path.basename(filename)
        d = d.split("_")[1].replace(".json", "")
        return d

    def print_stats(stats):
        for program in stats:
            print
            print program
            for phase in stats[program]:
                diff_sum = datetime.timedelta(0)
                for diff in stats[program][phase]:
                    diff_sum += diff
                print "%s: %s" % (phase, diff_sum / len(stats[program][phase]))

    stats = {}
    for filename in glob.glob("../datasets/dishwasher_*.json"):
        parser = DishwasherParser(single_run_testing=True)
        program = get_program(filename)
        if program not in stats:
            stats[program] = {}
        print filename
        content = json.load(open(filename))
        series = content["results"][0]["series"][0]["values"]
        latest_data = None
        for timestamp, value in series:
            timestamp = datetime.datetime.fromtimestamp(timestamp / 1000)
            data = parser.add_value(timestamp, value)
            if data is not None and data["current_phase"] is not None:
                latest_data = data
        print latest_data
        if latest_data:
            assert program in latest_data["current_program"]
            if program in ("quick", "prewash"):
                assert len(latest_data["current_program"]) == 1
            elif program in ("65C", "50C"):
                assert len(latest_data["current_program"]) == 2
            assert latest_data["current_phase"] == "finished"
            if latest_data["eta"] is not None:
                assert latest_data["eta"] == datetime.timedelta(0)
            for phase in latest_data["phases"]:
                if "diff" not in phase or phase["diff"] is None:
                    continue
                if phase["phase"] not in stats[program]:
                    stats[program][phase["phase"]] = []
                stats[program][phase["phase"]].append(phase["diff"])

    print_stats(stats)

if __name__ == '__main__':
    sys.exit(main())
