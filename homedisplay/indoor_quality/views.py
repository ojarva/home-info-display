
from .models import IndoorQuality
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import numpy
import time

class get_co2(View):
    def get(self, request, *args, **kwargs):
        data = IndoorQuality.objects.filter(timestamp__gte=now()-datetime.timedelta(hours=24))
        filtered_data = []
        co2_items = []
        temp_items = []
        for i, a in enumerate(data):
            co2_items.append(a.co2)
            temp_items.append(a.temperature)
            if i < 10:
                continue
            if i % 10 == 0:
                a.co2 = float(sum(co2_items)) / count(co2_items)
                a.temperature = float(sum(temp_items)) / count(co2_items)
                co2_items = []
                temp_items = []
                filtered_data.append(a)

        return HttpResponse(serializers.serialize("json", filtered_data), content_type="application/json")

class get_co2_trend(View):
    def get(self, request, *args, **kwargs):
        data = IndoorQuality.objects.all()[0:30]
        if len(data) < 30:
            return HttpResponse(json.dumps({"status": "no_data"}), content_type="application/json")
        co2 = []
        timestamps = []
        for item in data:
            if item.co2:
                co2.append(item.co2)
                timestamps.append(time.mktime(item.timestamp.timetuple()))
        co2.reverse()
        timestamps.reverse()
        timestamps = map(lambda x: x - timestamps[0], timestamps)
        co2 = numpy.array(co2)
        timestamps = numpy.array(timestamps)
        z = numpy.polyfit(timestamps, co2, 1)
        return HttpResponse(json.dumps({"delta": z[0], "base": z[1]}), content_type="application/json")
