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

    (state, _) = LightGroup.objects.get_or_create(group_id=group)
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

class control_per_source(View):
    BED = 1
    TABLE = 2
    KITCHEN = 3
    DOOR = 4

    def get(self, request, *args, **kwargs):
        source = kwargs.get("source")
        command = kwargs.get("command")
        if source == "door":
            if command == "night":
                led.off()
                for group in (self.DOOR, self.KITCHEN):
                    led.set_color("red", group)
                    led.set_brightness(10, group)
            elif command == "morning":
                led.off(self.BED)
                for group in (self.TABLE, self.KITCHEN, self.DOOR):
                    led.set_color("white", group)
                    led.set_brightness(10, group)
            elif command == "on":
                led.white()
                led.set_brightness(100)
            elif command == "off":
                led.set_brightness(0)
                led.off()
        elif source == "display":
            if command == "night":
                led.set_brightness(0)
                led.set_color("red")
                led.set_brightness(0)
            elif command == "morning-sleeping":
                led.off()
                led.white(self.KITCHEN)
                led.set_brightness(30, self.KITCHEN)
                led.white(self.DOOR)
                led.set_brightness(30, self.DOOR)
                led.set_color("red", self.TABLE)
                led.set_brightness(0, self.TABLE)
            elif command == "morning-all":
                led.white()
                led.set_brightness(30)
            elif command == "off":
                led.set_brightness(0)
                led.off()
            elif command == "on":
                led.white()
                led.set_brightness(100)
        else:
            raise NotImplementedError("Invalid source: %s" % source)
        return HttpResponse("ok")


class control(View):
    def get(self, request, *args, **kwargs):
        command = kwargs.get("command")
        group = int(kwargs.get("group"))

        if command == "on":
            led.white(group)
            led.set_brightness(100, group)
            update_lightstate(group, 100, "white")
        elif command == "off":
            led.set_brightness(0, group)
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
            (state, _) = LightGroup.objects.get_or_create(group_id=group)
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
