from django.shortcuts import render
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.conf import settings
from ledcontroller import LedController

led = LedController(settings.MILIGHT_IP)

class control(View):
    def get(self, request, *args, **kwargs):
        command = kwargs.get("command")
        group = int(kwargs.get("group"))

        if command == "on":
            led.white(group)
            led.set_brightness(100, group)
        elif command == "off":
            led.off(group)
        elif command == "morning":
            led.white(group)
            led.set_brightness(10, group)
        elif command == "disco":
            led.disco(group)
        elif command == "night":
            led.set_brightness(0, group)
            led.white(group)
            led.set_brightness(0, group)
            led.set_color("red", group)
            led.set_brightness(10, group)
        return HttpResponse("ok")
