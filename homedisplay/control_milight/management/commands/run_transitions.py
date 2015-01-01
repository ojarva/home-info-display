from control_milight.models import LightState, LightTransition
from control_milight.views import update_lightstate
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from ledcontroller import LedController
import datetime

#def update_lightstate(group, brightness, color, on=True):



class Command(BaseCommand):
    args = ''
    help = 'Run light transitions'

    def handle(self, *args, **options):
        led = LedController(settings.MILIGHT_IP)

        def execute_all(transition):
            led.set_brightness(transition.to_brightness, transition.group)
            if transition.to_color:
                led.set_color(transition.to_color, transition.group)
            if transition.to_nightmode:
                led.nightmode(transition.group)

            update_lightstate(transition.group, transition.to_brightness, transition.to_color)
            transition.delete()


        processed_lights = set()
        transitions = LightTransition.objects.all().order_by("priority")
        for transition in transitions:
            if transition.group in processed_lights:
                # Higher priority task for this lamp group was already executed.
                continue
            try:
                current_state = LightState.objects.get(group=transition.group)
            except LightState.DoesNotExist:
                execute_all(transition)
                continue

            time_left = (transition.end_time - now()).total_seconds()
            if time_left < 0:
                # Time ran out. Execute trest of the transition.
                execute_all(transition)
                continue

            if now() > transition.start_time:
                continue

            spent_time = (now() - transition.start_time).total_seconds()
            transition_length = (transition.end_time - transition.start_time).total_seconds()

            if transition.to_brightness is not None:
                brightness_range = transition.to_brightness - transition.start_brightness
                rate = brightness_range / transition_length
                set_brightness = transition.start_brightness + rate * spent_time
                led.set_brightness(set_brightness, transition.group)
            processed_lights.add(transition.group)
