from django.shortcuts import render
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.conf import settings
import time

from .models import Internet
class info(View):
    def get(self, request, *args, **kwargs):
        try:
            data = Internet.objects.latest()
        except Internet.DoesNotExist:
            return HttpResponse(json.dumps({"status": "error", "message": "No data available"}))
        age = int(time.mktime(data.update_timestamp.timetuple())*1000)

        ret = {"connected": data.connect_status, "signal": data.signal, "mode": data.mode, "age": age }
        return HttpResponse(json.dumps(ret), content_type="application/json")
