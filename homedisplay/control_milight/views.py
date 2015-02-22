from .models import LightGroup, LightAutomation, is_any_timed_running, update_lightstate
from display.views import run_display_command
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import View
from ledcontroller import LedController
import datetime
import json
import redis
import time

redis_instance = redis.StrictRedis()
led = LedController(settings.MILIGHT_IP)

class timed(View):
    def get_serialized_item(self, action):
        item = get_object_or_404(LightAutomation, action=action)
        ret = json.loads(serializers.serialize("json", [item]))
        ret[0]["fields"]["start_datetime"] = item.get_start_datetime().isoformat()
        ret[0]["fields"]["end_datetime"] = item.get_end_datetime().isoformat()
        for group in range(1, 5):
            if redis_instance.get("lightcontrol-no-automatic-%s" % group) is not None:
                ret[0]["fields"]["is_overridden"] = True
                break
        return ret

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
            item, created = LightAutomation.objects.get_or_create(action=action, defaults={"start_time": start_time, "duration": duration, "running": running})
            if not created:
                item.start_time = start_time
                item.duration = duration
                item.running = running

            item.save()
            serialized = self.get_serialized_item(action)
            redis_instance.publish("home:broadcast:generic", json.dumps({"key": "lightcontrol_timed_%s" % action, "content": serialized}))
            if is_any_timed_running() == False:
                # No timed lightcontrol is running (anymore). Delete overrides.
                for group in range(1, 5):
                    redis_instance.delete("lightcontrol-no-automatic-%s" % group)
                    redis_instance.publish("home:broadcast:generic", json.dumps({"key": "lightcontrol_timed_override", "content": {"action": "resume"}}))

            return HttpResponse(json.dumps(serialized), content_type="application/json")
        elif command == "override-resume":
            for group in range(1, 5):
                redis_instance.delete("lightcontrol-no-automatic-%s" % group)
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "lightcontrol_timed_override", "content": {"action": "resume"}}))
        item = self.get_serialized_item(action)
        return HttpResponse(json.dumps(item), content_type="application/json")


    def get(self, request, *args, **kwargs):
        action = kwargs.get("action")
        item = self.get_serialized_item(action)
        return HttpResponse(json.dumps(item), content_type="application/json")

class control_per_source(View):
    BED = 1
    TABLE = 2
    KITCHEN = 3
    DOOR = 4

    def get(self, request, *args, **kwargs):
        source = kwargs.get("source")
        command = kwargs.get("command")
        if source == "computer":
            if command == "night":
                led.set_brightness(0)
                led.set_color("red")
                led.set_brightness(0)
                update_lightstate(0, 0, "red")
            elif command == "morning-sleeping":
                led.off()
                update_lightstate(self.BED, None, None, False)
                led.white(self.KITCHEN)
                led.set_brightness(10, self.KITCHEN)
                update_lightstate(self.KITCHEN, 10, "white")
                led.white(self.DOOR)
                led.set_brightness(10, self.DOOR)
                update_lightsate(self.DOOR, 10, "white")
                led.set_color("red", self.TABLE)
                led.set_brightness(0, self.TABLE)
                update_lightstate(self.TABLE, 0, "red")
            elif command == "morning-wakeup":
                #TODO: fade up slowly
                led.white()
                run_display_command("on")
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "cancel"}))
                for a in range(0, 100, 5):
                    led.set_brightness(a)
                    time.sleep(0.5)
                update_lightstate(0, 100, "white")

            elif command == "off":
                led.set_brightness(0)
                led.off()
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "delay"}))
                update_lightstate(0, 0, False)
            elif command == "on":
                run_display_command("on")
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "cancel"}))
                led.white()
                led.set_brightness(100)
                update_lightstate(0, 100, "white")

        elif source == "door":
            if command == "night":
                led.off()
                update_lightstate(self.TABLE, None, None, False)
                update_lightstate(self.BED, None, None, False)
                for group in (self.DOOR, self.KITCHEN):
                    led.set_color("red", group)
                    led.set_brightness(10, group)
                    update_lightstate(group, 10, "red")

            elif command == "morning":
                led.off(self.BED)
                update_lightstate(self.BED, None, None, False)
                for group in (self.TABLE, self.KITCHEN, self.DOOR):
                    led.set_color("white", group)
                    led.set_brightness(10, group)
                    update_lightstate(group, 10, "white")

            elif command == "on":
                led.white()
                led.set_brightness(100)
                run_display_command("on")
                update_lightstate(0, 100, "white")
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "cancel"}))
            elif command == "off":
                led.set_brightness(0)
                led.off()
                update_lightstate(0, 0, None, False)
                led.white(self.DOOR)
                led.set_brightness(10, self.DOOR)
                update_lightstate(self.DOOR, 10, "white")
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "delay"}))
        elif source == "display":
            if command == "night":
                led.set_brightness(0)
                update_lightstate(0, 0)
                led.set_color("red")
                led.set_brightness(0)
                update_lightstate(0, 0, "red")
            elif command == "morning-sleeping":
                led.off()
                update_lightstate(self.BED, None, None, False)
                led.white(self.KITCHEN)
                led.set_brightness(10, self.KITCHEN)
                update_lightstate(self.KITCHEN, 10, "white")
                led.white(self.DOOR)
                led.set_brightness(10, self.DOOR)
                update_lightstate(self.DOOR, 10, "white")
                led.set_color("red", self.TABLE)
                led.set_brightness(0, self.TABLE)
                update_lightstate(self.TABLE, 10, "red")
            elif command == "morning-all":
                led.white()
                led.set_brightness(30)
                update_lightstate(0, 30, "white")
            elif command == "off":
                led.set_brightness(0)
                led.off()
                update_lightstate(0, 0, None, False)
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "delay"}))
            elif command == "on":
                redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "cancel"}))
                led.white()
                led.set_brightness(100)
                update_lightstate(0, 100, "white")
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
            update_lightstate(group, 0, None, False)
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
