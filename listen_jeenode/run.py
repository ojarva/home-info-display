"""Jeenode listener

Usage:
    run.py run [--debug] [--redis-host=<hostname>] [--redis-port=<port>]
"""
import local_settings as settings
from collections import namedtuple
import array
import json
import logging
import redis
import serial
import struct
import time


class JeenodeListener(object):
    def __init__(self, **kwargs):
        redis_args = {}
        if "redis_host" in kwargs and kwargs["redis_host"]:
            redis_args["host"] = kwargs["redis_host"]
        if "redis_port" in kwargs and kwargs["redis_port"]:
            redis_args["port"] = kwargs["redis_port"]
        self.redis = redis.StrictRedis(**redis_args)

        self.logger = logging.getLogger("listen-jeenode")
        if kwargs.get("debug"):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        format_string = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format_string)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def decode(self, fmt, data_tuple, data_string):
        coded_data = map(int, data_string.split())
        byte_string = array.array("B", coded_data).tostring()
        return data_tuple._make(struct.unpack(fmt, byte_string))

    def run(self):
        s = serial.Serial(settings.JEELINK, 57600)

        sent_event_map = {}
        queue_executed_at = time.time()

        while True:
            line = s.readline().strip()
            self.logger.info("Got '%s' from jeelink", line)
            if line.startswith("OK "):
                items = line.split(" ", 2)
                id = items[1]
                if id in settings.ITEM_MAP:
                    item_name = settings.ITEM_MAP[id]
                    if item_name in sent_event_map:
                        if sent_event_map[item_name] > time.time() - 5:
                            # Already triggered recently - no action
                            continue
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
                    self.logger.info("Processing trigger %s (%s)", item_name, id)
                    sent_event_map[item_name] = time.time()
                    self.redis.publish("lightcontrol-triggers-pubsub", json.dumps({"key": item_name}))

                elif id in settings.NODE_MAPPING:
                    node_data = settings.NODE_MAPPING[id]
                    decoded_data = self.decode(
                        node_data["fmt"], node_data["data"], items[2])
                    data = {
                        "timestamp": time.time(),
                        "data": decoded_data._asdict(),
                    }
                    coded_data = json.dumps(data)
                    if node_data.get("redis_queue"):
                        redis_instance.rpush(node_data["redis_queue"], coded_data)
                        self.logger.info("Pushed to %s: %s", node_data["redis_queue"], coded_data)
                    if node_data.get("redis_pubsub"):
                        redis_instance.publish(node_data["redis_pubsub"], coded_data)
                        self.logger.info("Published to %s: %s", node_data["redis_pubsub"], coded_data)
                else:
                    self.logger.warn("Unknown ID: %s", id)


def main(args):
    kwargs = {
        "redis_host": args.get("--redis-host"),
        "redis_port": args.get("--redis-post"),
    }
    lcs = JeenodeListener(debug=arguments.get("--debug", False), **kwargs)
    lcs.run()

if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='1.0')
    main(arguments)
