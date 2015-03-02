from django.core.management.base import BaseCommand, CommandError
from homedisplay.utils import publish_ws
import time
import json


class Command(BaseCommand):
    args = ''
    help = 'Reloads remote displays'

    def handle(self, *args, **options):
        publish_ws("reload", time.time())
