from django.core.management.base import BaseCommand, CommandError
from control_milight.utils import process_automatic_trigger
import serial
import time

class Command(BaseCommand):
    args = ''
    help = 'Listen for 433MHz radio messages'

    ITEM_MAP = {
        "5236713": "kitchen",
        "7697747": "hall",
        "1328959": "front-door",
        "247615": "unused-magnetic-switch",
    }

    def handle(self, *args, **options):
        s = serial.Serial("/dev/tty.usbserial-A9007LzM", 9600)
        sent_event_map = {}
        while True:
            line = s.readline()
            print "- %s" % line
            if line.startswith("Received "):
                id = line.split(" ")[1]
                if id in self.ITEM_MAP:
                    item_name = self.ITEM_MAP[id]
                    if item_name in sent_event_map:
                        if sent_event_map[item_name] > time.time() - 5:
                            print "Too recent event: %s" % item_name
                            continue
                    process_automatic_trigger(item_name)
                    sent_event_map[item_name] = time.time()
                else:
                    print "Unknown id: %s" % id
