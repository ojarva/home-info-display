from control_milight.models import LightGroup, LightTransition
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
            led.set_brightness(transition.to_brightness, transition.group.id)
            if transition.to_color:
                led.set_color(transition.to_color, transition.group.id)
            if transition.to_nightmode:
                led.nightmode(transition.group.id)

            update_lightstate(transition.group.id, transition.to_brightness, transition.to_color)
            transition.delete()


        processed_lights = set()
        transitions = LightTransition.objects.all().order_by("priority")
        for transition in transitions:

            if transition.group in processed_lights:
                # Higher priority task for this lamp group was already executed.
                continue
            try:
                current_state = transition.group
            except LightGroup.DoesNotExist:
                execute_all(transition)
                continue

            time_left = (transition.end_time - now()).total_seconds()
            if time_left < 0:
                # Time ran out. Execute the rest of the transition.
                execute_all(transition)
                continue

            if now() < transition.start_time:
                continue

            print "Processing %s" % transition


            spent_time = (now() - transition.start_time).total_seconds()
            transition_length = (transition.end_time - transition.start_time).total_seconds()

            if transition.to_brightness is not None:
                brightness_range = transition.to_brightness - transition.start_brightness
                rate = brightness_range / transition_length
                set_brightness = transition.start_brightness + rate * spent_time
                if int(set_brightness) != current_state.white_brightness: # TODO: per-color brightness value
                    led.set_brightness(set_brightness, transition.group.id)
                    print "Setting brightness %s for group %s" % (set_brightness, transition.group.id)
                    if current_state.color is None:
                        current_state.color = "white"
                    led.set_color(current_state.color, transition.group.id)
                update_lightstate(transition.group.id, set_brightness, current_state.color)

            processed_lights.add(transition.group.id)
