"""433Mhz listener

Usage:
    run.py run [--debug] [--redis-host=<hostname>] [--redis-port=<port>]
"""

import local_settings as settings
import datetime
import json
import logging
import redis
import serial
import time
import docopt


class Mhz433Listener(object):
    def __init__(self, **kwargs):
        redis_args = {}
        if "redis_host" in kwargs and kwargs["redis_host"]:
            redis_args["host"] = kwargs["redis_host"]
        if "redis_port" in kwargs and kwargs["redis_port"]:
            redis_args["port"] = kwargs["redis_port"]
        self.redis = redis.StrictRedis(**redis_args)

        self.logger = logging.getLogger("listen-433mhz")
        if kwargs.get("debug"):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        format_string = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_string)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def run(self):
        s = serial.Serial(settings.ARDUINO_433, 9600)

        ITEM_MAP = settings.ARDUINO_433_ITEM_MAP
        sent_event_map = {}
        while True:
            line = s.readline()
            if line.startswith("Received "):
                id = line.split(" ")[1]
                if id in ITEM_MAP:
                    item_name = ITEM_MAP[id]
                    if item_name in sent_event_map:
                        if sent_event_map[item_name] > time.time() - 5:
                            # Already triggered recently - no action
                            continue
                    self.logger.info("Processing trigger %s (%s)", item_name, id)
                    data = [{
                        "measurement": "triggers",
                        "time": datetime.datetime.utcnow().isoformat() + "Z",
                        "tags": {
                            "trigger": item_name,
                        },
                        "fields": {
                            "triggered": True,
                        },
                    }]
                    self.redis.publish("influx-update-pubsub", json.dumps(data))
                    sent_event_map[item_name] = time.time()
                    self.redis.publish("lightcontrol-triggers-pubsub", json.dumps({"key": item_name}))
                else:
                    self.logger.warn("Unknown ID: %s", id)


def main(args):
    kwargs = {
        "redis_host": args.get("--redis-host"),
        "redis_port": args.get("--redis-post"),
    }
    lcs = Mhz433Listener(debug=arguments.get("--debug", False), **kwargs)
    lcs.run()

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='1.0')
    main(arguments)
