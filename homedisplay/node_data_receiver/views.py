from .models import Task, get_repeating_data
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
import datetime
import json
import redis

redis_instance = redis.StrictRedis()


class Fridge(View):
    def get(self, request, *args, **kwargs):
        fridge_humidity = None
        fridge_temperature4 = None
        if humidity_data and len(humidity_data) > 0:
            if humidity_data[0] == "B":
                humidity_data = humidity_data.split("T")
                fridge_humidity = int(humidity_data[0][1:])
                fridge_temperature4 = float(humidity_data[1]) / 100
        fridge = kwargs.get("fridge")
        freezer = kwargs.get("freezer")
        if fridge is not None:
            fridge = fridge != "1"
        if freezer is not None:
            freezer = freezer != "1"

        data = {
            "fridge": fridge,
            "freezer": freezer,
            "fridge_temperature1": kwargs.get("t1"),
            "fridge_temperature2": kwargs.get("t2"),
            "fridge_temperature3": kwargs.get("t3"),
            "freezer_temperature1": kwargs.get("t_freezer1"),
            "humidity_data": kwargs.get("hd")
        }

        redis_instance.publish("fridge", json.dumps(data))

        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
