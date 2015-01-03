from django.shortcuts import render
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.conf import settings
from ledcontroller import LedController

from .models import LightGroup

led = LedController(settings.MILIGHT_IP)

def update_lightstate(group, brightness, color, on=True):
    if group == 0:
        for a in range(1, 5):
            update_lightstate(a, brightness, color)

    (state, _) = LightGroup.objects.get_or_create(pk=group)
    if brightness is not None:
        if color == "white":
            state.white_brightness = brightness
        else:
            state.rgb_brightness = brightness
    if color is not None:
        state.color = color
    state.on = on
    state.save()
    return state

class control(View):
    def get(self, request, *args, **kwargs):
        command = kwargs.get("command")
        group = int(kwargs.get("group"))

        if command == "on":
            led.white(group)
            led.set_brightness(100, group)
            update_lightstate(group, 100, "white")
        elif command == "off":
            led.off(group)
            update_lightstate(group, None, None, False)
        elif command == "morning":
            led.white(group)
            led.set_brightness(10, group)
            update_lightstate(group, 10, "white")
        elif command == "disco":
            led.disco(group)
            update_lightstate(group, None, "disco")
        elif command == "night":
            (state, _) = LightGroup.objects.get_or_create(pk=group)
            if state.color != "red":
                led.set_brightness(0, group)
                led.white(group)
                led.set_brightness(0, group)
            led.set_color("red", group)
            led.set_brightness(0, group)
            update_lightstate(group, 0, "red")
        else:
            raise NotImplementedError("Invalid command: %s" % command)
        return HttpResponse("ok")
