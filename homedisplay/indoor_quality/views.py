from .models import AirDataPoint, AirTimePoint
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import numpy
import time
from django.template import RequestContext
from django.shortcuts import render_to_response

class get_keys(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(settings.SENSOR_MAP.keys()), content_type="application/json")

class get_modal(View):
    def get(self, request, *args, **kwargs):
        ret = {"graphs": settings.SENSOR_MAP}
        return render_to_response("air_quality_graphs.html", ret, context_instance=RequestContext(request))

class get_json(View):
    def get(self, request, *args, **kwargs):
        data = AirDataPoint.objects.filter(timepoint__timestamp__gte=now()-datetime.timedelta(hours=24)).filter(name=kwargs["sensor_id"]).select_related("timepoint")
        if len(data) < 5:
            return HttpResponse(json.dumps([]), content_type="application/json")
        filtered_data = [{"value": float(data[0].value), "timestamp": str(data[0].timepoint.timestamp)}]
        items = []
        for i, a in enumerate(data[1:]):
            if a.value is None:
                continue
            items.append(a.value)
            if i < 5:
                continue
            if i % 5 == 0:
                a.value = round(float(sum(items)) / len(items), 1)
                items = []
                filtered_data.append({"value": float(a.value), "timestamp": str(a.timepoint.timestamp)})
        return HttpResponse(json.dumps(filtered_data), content_type="application/json")

class get_json_trend(View):
    def get(self, request, *args, **kwargs):
        data = AirDataPoint.objects.filter(name=kwargs["sensor_id"]).select_related("timepoint")[0:30]
        if len(data) < 30:
            return HttpResponse(json.dumps({"status": "no_data"}), content_type="application/json")
        items = []
        timestamps = []
        for item in data:
            if item.value is None:
                continue
            items.append(item.value)
            timestamps.append(time.mktime(item.timepoint.timestamp.timetuple()))
        items.reverse()
        timestamps.reverse()
        timestamps = map(lambda x: x - timestamps[0], timestamps)
        items = numpy.array(items)
        timestamps = numpy.array(timestamps)
        z = numpy.polyfit(timestamps, items, 1)
        return HttpResponse(json.dumps({"delta": z[0], "base": z[1]}), content_type="application/json")
