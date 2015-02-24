from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import View
from utorrent.client import UTorrentClient
import datetime
import json
import redis
import time

redis_instance = redis.StrictRedis()

def get_list_of_torrents():
    client = UTorrentClient(settings.UTORRENT, settings.UTORRENT_ADMIN, settings.UTORRENT_PASSWORD)
    status, data = client.list()
    if status != 200:
        return None
    items = []
    for item in data:
        items.append({"hash": item[0], "status": item[21], "filename": item[2], "size": item[3], "downloaded_percent": float(item[4]) / 10, "downloaded_bytes": item[5], "uploaded_bytes": item[6], "up_speed": item[8], "down_speed": item[9], "eta": item[10] })

    redis_instance.publish("home:broadcast:generic", json.dumps({"key": "torrent-list", "content": items}))
    return items

class List(View):
    def get(self, request, *args, **kwargs):
        items = get_list_of_torrents()
        return HttpResponse(json.dumps(items), content_type="application/json")

class Action(List):
    def post(self, request, *args, **kwargs):
        client = UTorrentClient(settings.UTORRENT, settings.UTORRENT_ADMIN, settings.UTORRENT_PASSWORD)
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
