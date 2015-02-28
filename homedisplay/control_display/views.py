from .utils import *
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
import json
import redis
import subprocess

redis_instance = redis.StrictRedis()

class Power(View):
    def post(self, request, *args, **kwargs):
        cmd = kwargs.get("command")
        if cmd in ("off", "on"):
            run_display_command(cmd)
        else:
            return HttpResponse("Invalid command")
        return HttpResponse("ok")

class Brightness(View):
    def post(self, request, *args, **kwargs):
        set_destination_brightness(float(kwargs.get("brightness")))
        return HttpResponse("ok")


class RestartBrowser(View):
    def post(self, request, *args, **kwargs):
        p = subprocess.Popen(["killall", "chromium"])
        p.wait()
        env = {"DISPLAY": ":0"}
        p = subprocess.Popen(["chromium-browser", "--touch-events=enabled", "--start-fullscreen", "--disable-session-crashed-bubble", "--disable-touch-drag-drop", "--disable-pinch"])
        p.wait()
        return HttpResponse("ok")
