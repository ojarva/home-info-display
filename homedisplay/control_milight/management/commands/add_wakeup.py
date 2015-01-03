from control_milight.models import LightGroup, LightTransition
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
import datetime




class Command(BaseCommand):
    args = ''
    help = 'Add morning transition'

    def handle(self, *args, **options):
        start_time = now() + datetime.timedelta(minutes=float(args[0]) * 60)
        for a in range(1, 4):
            (lightgroup, _) = LightGroup.objects.get_or_create(pk=a)
            transition = LightTransition(group=lightgroup, description="Morning wakeup", start_time=start_time, end_time=start_time+datetime.timedelta(minutes=30), start_brightness=0, to_brightness=100)
            transition.save()
