from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.core import serializers

from .models import IndoorQuality
import numpy
import json
import time

class get_co2(View):
    def get(self, request, *args, **kwargs):
        data = IndoorQuality.objects.all()[0:1440]
        return HttpResponse(serializers.serialize("json", data), content_type="application/json")

class get_co2_trends(View):
    def get(self, request, *args, **kwargs):
        data = IndoorQuality.objects.all()[0:30]
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
