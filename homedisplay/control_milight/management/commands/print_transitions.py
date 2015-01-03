from control_milight.models import LightGroup, LightTransition
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
import datetime




class Command(BaseCommand):
    args = ''
    help = 'List transitions'

    def handle(self, *args, **options):
        for transition in LightTransition.objects.all().order_by("start_time"):
            print "Group: %s, start time: %s, end time: %s, brightness from %s to %s" % (transition.group, transition.start_time, transition.end_time, transition.start_brightness, transition.to_brightness)
