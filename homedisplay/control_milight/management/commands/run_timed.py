from django.core.management.base import BaseCommand, CommandError
from control_milight.utils import run_timed_actions

class Command(BaseCommand):
    args = ''
    help = 'Run timed transitions'

    def handle(self, *args, **options):
        run_timed_actions()
