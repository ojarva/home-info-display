from control_milight.models import LightGroup, LightTransition
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
import datetime




class Command(BaseCommand):
    args = ''
    help = 'Add evening transition'

    def handle(self, *args, **options):
        start_time = now()
        for a in range(1, 4):
            (lightgroup, _) = LightGroup.objects.get_or_create(group_id=a)
            transition = LightTransition(group=lightgroup, description="Evening", start_time=start_time, end_time=start_time+datetime.timedelta(minutes=float(args[0]) * 60), start_brightness=100, to_brightness=0)
            transition.save()
