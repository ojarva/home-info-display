from django.http import HttpResponse
from django.views.generic import View
import datetime
import json
import redis

redis_instance = redis.StrictRedis()


class Fridge(View):
    def get(self, request, *args, **kwargs):
        def format_number(number):
            if number is None:
                return None
            else:
                value = float(number)
                if value == -127:
                    return None
                return value
        fridge_humidity = None
        fridge_temperature4 = None
        humidity_data = request.GET.get("hd")
        if humidity_data and len(humidity_data) > 0:
            if humidity_data[0] == "B":
                humidity_data = humidity_data.split("T")
                fridge_humidity = int(humidity_data[0][1:])
                fridge_temperature4 = float(humidity_data[1]) / 100
        fridge = request.GET.get("fridge")
        freezer = request.GET.get("freezer")
        if fridge is not None:
            fridge = fridge == "1"
        if freezer is not None:
            freezer = freezer == "1"

        data = {
            "data": {
                "fridge_door_open": fridge,
                "freezer_door_open": freezer,
                "fridge_temperature1": format_number(request.GET.get("t1")),
                "fridge_temperature2": format_number(request.GET.get("t2")),
                "fridge_temperature3": format_number(request.GET.get("t3")),
                "freezer_temperature1": format_number(request.GET.get("t_freezer1")),
                "fridge_humidity": fridge_humidity,
                "fridge_temperature4": fridge_temperature4,
            }
        }

        redis_instance.publish("fridge-inside-pubsub", json.dumps(data))

        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
