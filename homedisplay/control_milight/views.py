from .models import LightGroup, LightAutomation, is_any_timed_running, update_lightstate, get_serialized_timed_action, get_serialized_lightgroup, get_serialized_lightgroups, get_main_buttons, is_group_on
from .utils import run_timed_actions, convert_group_to_automatic, get_current_settings_for_light, sync_lightstate
from control_display.display_utils import run_display_command
from control_display.utils import initiate_delayed_shutdown, set_destination_brightness
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import View
from homedisplay.utils import publish_ws
from ledcontroller import LedController
from server_power.views import sp
import datetime
import json
import redis
import time

redis_instance = redis.StrictRedis()
led = LedController(settings.MILIGHT_IP)


def set_light_group_delayed_off(group):
    on_until = timezone.now() + datetime.timedelta(seconds=15)
    convert_group_to_automatic(group, on_until)


class TimedProgram(View):

    def post(self, request, *args, **kwargs):
        action = kwargs.get("action")
        command = kwargs.get("command")
        if command == "update":
            start_time = request.POST.get("start_time").split(":")
            duration = request.POST.get("duration").replace("+", "").split(":")
            running = request.POST.get("running")
            if running == "true":
                running = True
            else:
                running = False
            start_time = datetime.time(int(start_time[0]), int(start_time[1]))
            duration = int(duration[0]) * 3600 + int(duration[1]) * 60
            item, created = LightAutomation.objects.get_or_create(action=action, defaults={
                                                                  "start_time": start_time, "duration": duration, "running": running})
            if not created:
                item.start_time = start_time
                item.duration = duration
                item.running = running

            item.save()
            if is_any_timed_running() == False:
                # No timed lightcontrol is running (anymore). Delete overrides.
                for group in range(1, 5):
                    redis_instance.delete(
                        "lightcontrol-no-automatic-%s" % group)
                    publish_ws("lightcontrol-timed-override",
                               {"action": "resume"})
            else:
                run_timed_actions()
            return HttpResponse(json.dumps(get_serialized_timed_action(item)), content_type="application/json")
        elif command == "override-resume":
            for group in range(1, 5):
                redis_instance.delete("lightcontrol-no-automatic-%s" % group)
                publish_ws("lightcontrol-timed-override", {"action": "resume"})
            run_timed_actions()
        instance = get_object_or_404(LightAutomation, action=action)
        item = get_serialized_timed_action(instance)
        return HttpResponse(json.dumps(item), content_type="application/json")

    def get(self, request, *args, **kwargs):
        action = kwargs.get("action")
        instance = get_object_or_404(LightAutomation, action=action)
        item = get_serialized_timed_action(instance)
        return HttpResponse(json.dumps(item), content_type="application/json")


class ControlPerSource(View):
    BED = 1
    TABLE = 2
    KITCHEN = 3
    DOOR = 4

    def post(self, request, *args, **kwargs):
        source = kwargs.get("source")
        command = kwargs.get("command")
        if command == "sync":
            sync_lightstate()
        elif source == "computer":
            if command == "night":
                led.set_brightness(0)
                led.set_color("red")
                led.set_brightness(0)
                update_lightstate(0, 0, "red")
            elif command == "off":
                set_light_group_delayed_off(0)
                initiate_delayed_shutdown()
            elif command == "morning":
                led.set_color("white")
                led.set_brightness(10)
                update_lightstate(0, 10, "white")
            elif command == "on":
                run_display_command("on")
                led.white()
                led.set_brightness(100)
                update_lightstate(0, 100, "white")
            elif command == "off-all":
                set_light_group_delayed_off(0)
                initiate_delayed_shutdown()
                sp.shutdown()  # Shutdown server
                # TODO: shut down speakers

        elif source == "door":
            if command == "night":
                led.off()
                update_lightstate(self.TABLE, None, None, False)
                update_lightstate(self.BED, None, None, False)
                for group in (self.DOOR, self.KITCHEN):
                    led.set_color("red", group)
                    led.set_brightness(10, group)
                    update_lightstate(group, 10, "red")
            elif command == "on":
                run_display_command("on")
                led.white()
                led.set_brightness(100)
                update_lightstate(0, 100, "white")
            elif command == "morning":
                led.set_color("white")
                led.set_brightness(10)
                update_lightstate(0, 10, "white")
            elif command == "off":
                set_light_group_delayed_off(0)
                initiate_delayed_shutdown()
        elif source == "display":
            if command == "night":
                if is_group_on(0):
                    led.set_brightness(0)
                    update_lightstate(0, 0)
                led.set_color("red")
                led.set_brightness(0)
                update_lightstate(0, 0, "red")
            elif command == "morning":
                led.set_color("white")
                led.set_brightness(10)
                update_lightstate(0, 10, "white")
            elif command == "off":
                set_light_group_delayed_off(0)
                initiate_delayed_shutdown()
            elif command == "on":
                run_display_command("on")
                led.white()
                led.set_brightness(100)
                update_lightstate(0, 100, "white")
        else:
            raise NotImplementedError("Invalid source: %s" % source)
        set_destination_brightness()
        return HttpResponse(json.dumps(get_serialized_lightgroups()), content_type="application/json")


class Control(View):

    def post(self, request, *args, **kwargs):
        command = kwargs.get("command")
        group = int(kwargs.get("group"))

        if command == "on":
            led.white(group)
            led.set_brightness(100, group)
            update_lightstate(group, 100, "white")
            if group == 0:
                run_display_command("on")
        elif command == "off":
            set_light_group_delayed_off(group)
            if group == 0:
                # Shut down display if all lights were turned off.
                initiate_delayed_shutdown()
        elif command == "auto-brightness":
            def execute(group_id):
                brightness, color = get_current_settings_for_light(group_id)
                led.set_color(color, group)
                led.set_brightness(brightness, group)
                update_lightstate(group, brightness, color)

            if group == 0:
                for group in range(1, 5):
                    execute(group)
            else:
                execute(group)
        elif command == "disco":
            led.disco(group)
            update_lightstate(group, None, "disco")
        elif command == "night":
            def execute(group):
                (state, _) = LightGroup.objects.get_or_create(group_id=group)
                if state.color != "red":
                    led.set_brightness(0, group)
                    led.white(group)
                    led.set_brightness(0, group)
                led.set_color("red", group)
                led.set_brightness(0, group)
                update_lightstate(group, 0, "red")

            if group == 0:
                for group in range(1, 5):
                    execute(group)
            else:
                execute(group)
        elif command == "brightness":
            brightness = int(kwargs.get("parameter"))
            led.set_brightness(brightness, group)
            update_lightstate(group, brightness)
        elif command == "sync":
            sync_lightstate()
        else:
            raise NotImplementedError("Invalid command: %s" % command)
        set_destination_brightness()
        return HttpResponse(json.dumps(get_serialized_lightgroups()), content_type="application/json")

    def get(self, request, *args, **kwargs):
        group = int(kwargs.get("group", 0))
        items = LightGroup.objects.all()
        if group is not 0:
            items = items.filter(group_id=group)
        serialized = {"groups": [get_serialized_lightgroup(a) for a in items],
                      "main_buttons": get_main_buttons()
                      }
        return HttpResponse(json.dumps(serialized), content_type="application/json")
