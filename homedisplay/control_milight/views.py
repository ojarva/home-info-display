from control_display.display_utils import run_display_command
from control_display.utils import initiate_delayed_shutdown, set_destination_brightness
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import View
from homedisplay.utils import publish_ws
from server_power.views import sp
import datetime
import json
import redis
import time

redis_instance = redis.StrictRedis()


def send_lightcontrol_command(command, group, source="manual", **kwargs):
    data = {
        "source": source,
        "command": command,
        "group": group,
    }
    data.update(kwargs)
    redis_instance.publish("lightcontrol-control-pubsub", json.dumps(data))


def get_lightprogram(action):
    redis_key = "lightcontrol-program-%s" % action
    data = json.loads(redis_instance.get(redis_key))
    data["next_start_at"] = redis_instance.get("%s-next_start_at" % redis_key)
    data["next_end_at"] = redis_instance.get("%s-next_end_at" % redis_key)
    data["running"] = redis_instance.get("lightprogram-%s-running" % action) not in ("False", "false")
    return data


def get_lightgroup(group_id):
    redis_key = "lightcontrol-state-%s" % group_id
    color = redis_instance.get("%s-color" % redis_key)
    if color != "white":
        brightness_key = "rgb"
    else:
        brightness_key = "white"
    brightness = redis_instance.get("%s-%s_brightness" % (redis_key, brightness_key))
    data = {
        "on": redis_instance.get("%s-on" % redis_key) in ("true", "True"),
        "name": redis_instance.get("lightcontrol-group-%s-name" % group_id),
        "color": color,
        "current_brightness": brightness,
        "id": group_id,
    }
    return data


class TimedProgram(View):

    def post(self, request, *args, **kwargs):
        action = kwargs.get("action")
        command = kwargs.get("command")
        if command == "update":
            start_time = request.POST.get("start_time").split(":")
            duration = request.POST.get("duration").replace("+", "").split(":")
            start_time = datetime.time(int(start_time[0]), int(start_time[1]))
            duration = int(duration[0]) * 3600 + int(duration[1]) * 60
            current_settings = json.loads(redis_instance.get("lightcontrol-program-%s" % action))
            current_settings["duration"] = duration
            current_settings["start_at"] = start_time.strftime("%H:%M")
            redis_instance.set("lightcontrol-program-%s" % action, json.dumps(current_settings))

            if "running" in request.POST:
                running = request.POST.get("running")
                running = running in ("true", "True", "1")
                redis_instance.set("lightprogram-%s-running" % action, running)
                if running:
                    for group in range(1, 5):
                        redis_instance.set("lightcontrol-state-%s-auto" % group, True)

            send_lightcontrol_command("program-sync", 0)
            data = get_lightprogram(action)
            publish_ws("lightcontrol-timed-%s" % action, data)
            return HttpResponse(json.dumps(data), content_type="application/json")
        elif command == "override-resume":
            for group in range(1, 5):
                redis_instance.set("lightcontrol-state-{group}-auto".format(group=group), True)
                send_lightcontrol_command("program-sync", 0)
                publish_ws("lightcontrol-timed-override", {"action": "resume"})

        # TODO: get and serialize program details
        item = get_lightprogram(action)
        return HttpResponse(json.dumps(item), content_type="application/json")

    def get(self, request, *args, **kwargs):
        action = kwargs.get("action")
        item = get_lightprogram(action)
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
            send_lightcontrol_command("sync", 0)
        elif source == "computer":
            if command == "night":
                send_lightcontrol_command("night", 0)
            elif command == "off":
                send_lightcontrol_command("off", 0)
                initiate_delayed_shutdown()
            elif command == "on":
                run_display_command("on")
                send_lightcontrol_command("on", 0)
                send_lightcontrol_command("set_color", 0, color="white")
                send_lightcontrol_command("set_brightness", 0, brightness=100)
            elif command == "off-all":
                send_lightcontrol_command("off", 0)
                initiate_delayed_shutdown()
                sp.shutdown()  # Shutdown server

        elif source == "door":
            if command == "night":
                send_lightcontrol_command("night", 0)
            elif command == "on":
                run_display_command("on")
                send_lightcontrol_command("on", 0)
                send_lightcontrol_command("set_color", 0, color="white")
                send_lightcontrol_command("set_brightness", 0, brightness=100)
            elif command == "off":
                send_lightcontrol_command("off", 0)
                initiate_delayed_shutdown()
        elif source == "display":
            if command == "night":
                send_lightcontrol_command("night", 0)
            elif command == "off":
                send_lightcontrol_command("off", 0)
                initiate_delayed_shutdown()
            elif command == "on":
                run_display_command("on")
                send_lightcontrol_command("on", 0)
                send_lightcontrol_command("set_color", 0, color="white")
                send_lightcontrol_command("set_brightness", 0, brightness=100)
        else:
            raise NotImplementedError("Invalid source: %s" % source)
        set_destination_brightness()
        return HttpResponse(json.dumps({"ok": True}), content_type="application/json")


class Control(View):

    def post(self, request, *args, **kwargs):
        command = kwargs.get("command")
        group = int(kwargs.get("group"))

        if command == "on":
            send_lightcontrol_command("on", group)
            send_lightcontrol_command("set_color", group, color="white")
            send_lightcontrol_command("set_brightness", group, brightness=100)
            if group == 0:
                run_display_command("on")
        elif command == "off":
            send_lightcontrol_command("off", group)
            if group == 0:
                # Shut down display if all lights were turned off.
                initiate_delayed_shutdown()
        elif command == "night":
            send_lightcontrol_command("night", group)
        elif command == "brightness":
            brightness = int(kwargs.get("parameter"))
            send_lightcontrol_command("set_brightness", group, brightness=brightness)
        elif command == "sync":
            send_lightcontrol_command("sync", group)
        else:
            raise NotImplementedError("Invalid command: %s" % command)
        set_destination_brightness()
        return HttpResponse(json.dumps({"ok": True}), content_type="application/json")

    def get(self, request, *args, **kwargs):
        data = []
        for group_id in range(1, 5):
            data.append(get_lightgroup(group_id))
        return HttpResponse(json.dumps({"groups": data}), content_type="application/json")
