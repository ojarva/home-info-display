from django.core.management.base import BaseCommand, CommandError

import redis
import time
import json


class Command(BaseCommand):
    args = ''
    help = 'Reloads remote displays'

    def handle(self, *args, **options):
        r = redis.StrictRedis()
        r.publish("home:broadcast:generic", json.dumps({"key": "reload", "content": time.time()}))
