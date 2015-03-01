from .tasks import *
from .utils import *
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import View
from homedisplay.celery import app as celery_app
import json
import redis
import subprocess

redis_instance = redis.StrictRedis()

def cancel_delayed_task():
    display_task = redis_instance.get("display-control-task")
    redis_instance.delete("display-control-command")
    if display_task:
        celery_app.control.revoke(display_task)
        redis_instance.delete("display-control-task")
        return display_task
    return False

class Power(View):
    def post(self, request, *args, **kwargs):

        cmd = kwargs.get("command")
        if cmd in ("off", "on"):
            # Revoke possible delayed tasks
            cancel_delayed_task()
            run_display_command(cmd)
            return HttpResponse("ok")

        if cmd == "delayed-shutdown":
            cancel_delayed_task()
            redis_instance.setex("display-control-command", 120, "off")
            display_task = run_display_command_task.apply_async(countdown=30, expires=120)
            redis_instance.set("display-control-task", display_task.task_id)
            redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "delayed-shutdown"}))
            return HttpResponse("ok")
        elif cmd == "cancel-delayed":
            display_task = cancel_delayed_task()
            redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "cancel-delayed"}))
            if display_task:
                return HttpResponse("Revoked %s" % display_task)
            return HttpResponse("No task available")

        return HttpResponse("Invalid command")



class Brightness(View):
    def post(self, request, *args, **kwargs):
        set_destination_brightness(float(kwargs.get("brightness")))
        return HttpResponse("ok")


class RestartBrowser(View):
    def post(self, request, *args, **kwargs):
        p = subprocess.Popen(["killall", "chromium-browser"])
        p.wait()
        env = {"DISPLAY": ":0"}
        p = subprocess.Popen(["chromium-browser", "--touch-events=enabled", "--start-fullscreen", "--disable-session-crashed-bubble", "--disable-touch-drag-drop", "--disable-pinch"], env=env, shell=True)
        p.wait()
        return HttpResponse("ok")
