from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import redis
import time

redis_instance = redis.StrictRedis()

class List(View):
    def get(self, request, *args, **kwargs):
        items = get_list_of_torrents()
        return HttpResponse(json.dumps(items), content_type="application/json")

class Action(List):
    def post(self, request, *args, **kwargs):
        command = kwargs.get("command")
        hash = kwargs.get("hash")
        if command == "remove":
            client.remove(hash)
        elif command == "stop":
            client.stop(hash)
        elif command == "start":
            client.start(hash)
        else:
            return HttpResponse(json.dumps({"success": False, "status": "Invalid command"}), content_type="application/json")
        items = get_list_of_torrents()
        return HttpResponse(json.dumps({"success": True, "status": "Executed %s for %s" % (command, hash), "content": items}), content_type="application/json")
