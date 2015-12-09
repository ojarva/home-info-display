from collections import namedtuple
from control_milight.utils import process_automatic_trigger
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import array
import json
import logging
import redis
import serial
import struct
import time

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

class Command(BaseCommand):
    args = ''
    help = 'Listen for jeenode messages'

    NODE_MAPPING = {
        "4": # Dishwasher
            {
                "item": "dishwasher",
                "data": namedtuple("Dishwasher", "power_consumption"),
                "fmt": "f",
                "redis_pubsub": "dishwasher-pubsub",
            },
        "5": # Dust node
            {
                "item": "dust",
                "data": namedtuple("AirNode", "room_humidity room_temperature barometer_temperature barometer_reading dust_density"),
                "fmt": "fffff",
                "redis_pubsub": "dust-node-pubsub",
            },
        "6": # microwave
            {
                "item": "microwave",
                "data": namedtuple("Microwave", "power_consumption door"),
                "fmt": "fb",
                "redis_pubsub": "microwave-pubsub",
            }
    }

    ITEM_MAP = {
        "7": "table-acceleration-sensor"
    }

    def decode(self, fmt, data_tuple, data_string):
        coded_data = map(int, data_string.split())
        byte_string = array.array("B", coded_data.tostring())
        return data_tuple._make(struct.unpack(fmt, byte_string))

    def handle(self, *args, **options):
        redis_instance = redis.StrictRedis()

        s = serial.Serial(settings.JEELINK, 57600)
        queue = []
        slow_queue = []

        def execute_queue():
            # Run items with changes first. Reads more items if anything is available from serial port.
            executed_items = set()

            # First, execute all led commands only once - more unreliable but faster.
            while len(queue) > 0:
                if s.inWaiting() != 0:
                    return
                priority, item = queue.pop()
                if item in executed_items:
                    continue
                executed_items.add(item)
                process_automatic_trigger(item, quick=True)
                slow_queue.append((priority, item))

            # Execute all queue items again, with multiple repetitions to ensure everything will succeed.
            executed_items = set()
            while len(slow_queue) > 0:
                if s.inWaiting() != 0:
                    return
                priority, item = slow_queue.pop()
                if item in executed_items:
                    continue
                executed_items.add(item)
                process_automatic_trigger(item)


        sent_event_map = {}
        queue_executed_at = time.time()

        while True:
            if s.inWaiting() == 0:
                # No more data to read -> execute queue, if any.
                queue = sorted(queue)
                slow_queue = sorted(slow_queue)

                execute_queue()

            line = s.readline().strip()
            print "Received '%s'" % line
            logger.info("Got '%s' from jeelink" % line)
            if line.startswith("OK "):
                items = line.split(" ", 2)
                id = items[1]
                if id in ITEM_MAP:
                    item_name = ITEM_MAP[id]
                    if item_name in sent_event_map:
                        if sent_event_map[item_name] > time.time() - 5:
                            # Already triggered recently - no action
                            continue
                    logger.info("Processing trigger %s (%s)", item_name, id)
                    should_execute_something = process_automatic_trigger(item_name, False)
                    sent_event_map[item_name] = time.time()
                    if should_execute_something:
                        prio = 1
                    else:
                        prio = 2
                    queue.append((should_execute_something, item_name))
                elif id in NODE_MAPPING:
                    node_data = NODE_MAPPING[id]
                    decoded_data = decode(node_data["fmt"], node_data["data"], items[3])
                    data = {
                        "timestamp": time.time(),
                        "data": decoded_data._asdict(),
                    }
                    coded_data = json.dumps(data)
                    if node_data.get("redis_queue"):
                        redis_instance.rpush(node_data["redis_queue"], coded_data)
                    if node_data.get("redis_pubsub"):
                        redis_instance.publish(node_data["redis_pubsub"], coded_data)
                else:
                    logger.warn("Unknown ID: %s", id)
