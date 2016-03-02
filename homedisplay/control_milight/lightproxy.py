from django.conf import settings
from django.utils import timezone
from homedisplay.utils import publish_ws
from ledcontroller import LedController
from .models import *


class LightState(object):

    def get(self, group):
        pass

    def set_on(self, group, brightness, color, **kwargs):
        pass

    def set_off(self, group, **kwargs):
        pass


class LightProxy(object):

    def __init__(self):
        self.led = LedController(settings.MILIGHT_IP)
        self.lightstate = LightState()

    def set_state(self, group, power_state, color, brightness, automatic, **kwargs):
        if group == 0:
            for group
        current_state = self.ligtstate.get(group)

    def delayed_off(self, group):
        from control_milight.utils import convert_group_to_automatic
        on_until = timezone.now() + datetime.timedelta(seconds=15)
        convert_group_to_automatic(group, on_until)
