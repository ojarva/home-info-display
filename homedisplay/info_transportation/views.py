from django.http import HttpResponse
from django.views.generic import View
import json
import redis
import requests

redis_instance = redis.StrictRedis()

class GetJson(View):
    """ Returns next departures per stop, only for currently active lines. """
    def get(self, request, *args, **kwargs):
        data = redis_instance.get("realtime-bus")
        if data:
            data = json.loads(data)
        else:
            data = []
        return HttpResponse(json.dumps(data), content_type="application/json")

class GetData(View):
    def get(self, request, *args, **kwargs):
        resp = requests.get("http://localhost:5019/" + kwargs.get("url"))
        return HttpResponse(resp.content, content_type=resp.headers.get('content-type'))

class Poikkeustiedotteet(View):
    def get(self, request, *args, **kwargs):
        data = redis_instance.get("hsl-poikkeusinfo")
        return HttpResponse(data, content_type="application/json")
