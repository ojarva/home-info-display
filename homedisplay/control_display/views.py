from .utils import *
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
import json
import redis

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
        return self.get(request, *args, **kwargs)
