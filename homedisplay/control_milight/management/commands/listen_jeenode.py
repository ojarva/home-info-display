from control_milight.utils import process_automatic_trigger
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import serial
import time
import logging

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

class Command(BaseCommand):
    args = ''
    help = 'Listen for jeenode messages'

    def handle(self, *args, **options):
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
        ITEM_MAP = {
            "7": "table-acceleration-sensor"
        }

        while True:
            if s.inWaiting() == 0:
                # No more data to read -> execute queue, if any.
                queue = sorted(queue)
                slow_queue = sorted(slow_queue)

                execute_queue()

            line = s.readline()
            if line.startswith("OK "):
                items = line.split(" ")
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
                else:
                    logger.warn("Unknown ID: %s", id)
