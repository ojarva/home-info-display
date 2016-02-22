from django.http import HttpResponse
from django.views.generic import View
import json
import redis

redis_instance = redis.StrictRedis()

class get_json(View):
    """ Returns next departures per stop, only for currently active lines. """
    def get(self, request, *args, **kwargs):
        data = redis_instance.get("realtime-bus")
        if data:
            data = json.loads(data)
        else:
            data = []
        return HttpResponse(json.dumps(data), content_type="application/json")
