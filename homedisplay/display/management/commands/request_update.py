from django.core.management.base import BaseCommand, CommandError

import redis
import time

r = redis.StrictRedis()

class Command(BaseCommand):
    args = ''
    help = 'Reloads remote displays'

    def handle(self, *args, **options):
        r.publish("home:broadcast:reload", time.time())
