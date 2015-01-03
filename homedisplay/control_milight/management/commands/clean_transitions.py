from control_milight.models import LightGroup, LightTransition
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = ''
    help = 'Cleans transitions'

    def handle(self, *args, **options):
        print LightTransition.objects.all().delete()
