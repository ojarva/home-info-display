from django.http import HttpResponse
from django.views.generic import View
import datetime
import json
import redis

redis_instance = redis.StrictRedis()


class Status(View):

    def get(self, request, *args, **kwargs):
        status = redis_instance.get("kettle-info")
        return HttpResponse(status, content_type="application/json")


class Control(View):

    def post(self, request, *args, **kwargs):
        def run_kettle_command(data):
            redis_instance.publish("kettle-commands", json.dumps(data))
            return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
        command = kwargs.get("command")
        arg = kwargs.get("arg")
        if command == "on":
            # TODO: check water level
            if arg is not None:
                temperature = int(arg)
            else:
                temperature = 100
            return run_kettle_command({"on": temperature})
        if command == "off":
            return run_kettle_command({"off": True})
