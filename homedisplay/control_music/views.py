from django.http import HttpResponse
from django.views.generic import View
from homedisplay.utils import publish_ws
import json
import redis

redis_instance = redis.StrictRedis()

# Store/retrieve rdio player state
class PlayState(View):
    def post(self, request, *args, **kwargs):
        redis_instance.setex("rdio-state", 600, kwargs.get("state"))
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse(redis_instance.get("rdio-state"))

class PlayPosition(View):
    def post(self, request, *args, **kwargs):
        redis_instance.setex("rdio-position", 120, kwargs.get("position"))
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse(redis_instance.get("rdio-position"))

class PlayingTrack(View):
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pass


# Control rdio player
class PlayControl(View):
    def post(self, request, *args, **kwargs):
        publish_ws("rdio-control", kwargs)

# Control queue items
class Queue(View):
    def post(self, request, *args, **kwargs):
        publish_ws("rdio-control", kwargs)
