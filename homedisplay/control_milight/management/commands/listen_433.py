from control_milight.utils import process_automatic_trigger
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from influxdb import InfluxDBClient
import datetime
import json
import logging
import redis
import serial
import time

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class Command(BaseCommand):
    args = ''
    help = 'Listen for 433MHz radio messages'

    def handle(self, *args, **options):
        s = serial.Serial(settings.ARDUINO_433, 9600)
        queue = []
        slow_queue = []
        redis_instance = redis.StrictRedis()
        influx_client = InfluxDBClient("localhost", 8086, "root", "root", "home")

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


        ITEM_MAP = settings.ARDUINO_433_ITEM_MAP
        sent_event_map = {}
        queue_executed_at = time.time()
        while True:
            if s.inWaiting() == 0:
                # No more data to read -> execute queue, if any.
                queue = sorted(queue)
                slow_queue = sorted(slow_queue)

                execute_queue()

            line = s.readline()
            if line.startswith("Received "):
                id = line.split(" ")[1]
                if id in ITEM_MAP:
                    item_name = ITEM_MAP[id]
                    if item_name in sent_event_map:
                        if sent_event_map[item_name] > time.time() - 5:
                            # Already triggered recently - no action
                            continue
                    logger.info("Processing trigger %s (%s)", item_name, id)
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
                    redis_instance.publish("influx-update-pubsub", json.dumps(data, cls=DateTimeEncoder))
                    try:
                        influx_client.write_points(data)
                    except Exception as err:
                        logger.info("Pushing to influxdb failed: %s. Ignoring." % err)
                    should_execute_something = process_automatic_trigger(item_name, False)
                    sent_event_map[item_name] = time.time()
                    if should_execute_something:
                        prio = 1
                    else:
                        prio = 2
                    queue.append((should_execute_something, item_name))
                else:
                    logger.warn("Unknown ID: %s", id)
