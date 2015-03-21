from control_milight.utils import process_automatic_trigger
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import serial
import time
import logging

logger = logging.getLogger("%s.%s" % ("homecontroller", __name__))

class Command(BaseCommand):
    args = ''
    help = 'Listen for 433MHz radio messages'

    def handle(self, *args, **options):
        s = serial.Serial(settings.ARDUINO_433, 9600)
        ITEM_MAP = settings.ARDUINO_433_ITEM_MAP
        sent_event_map = {}
        while True:
            line = s.readline()
            if line.startswith("Received "):
                id = line.split(" ")[1]
                if id in self.ITEM_MAP:
                    item_name = self.ITEM_MAP[id]
                    if item_name in sent_event_map:
                        if sent_event_map[item_name] > time.time() - 5:
                            continue
                    logger.info("Processing trigger %s (%s)", item_name, id)
                    process_automatic_trigger(item_name)
                    sent_event_map[item_name] = time.time()
                else:
                    logger.warn("Unknown ID: %s", id)
