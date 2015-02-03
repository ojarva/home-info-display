from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import View
import time
from django.core import serializers
import json

from .models import Internet
class info(View):
    def get(self, request, *args, **kwargs):
        try:
            data = Internet.objects.latest()
        except Internet.DoesNotExist:
            return HttpResponse(json.dumps({"status": "error", "message": "No data available"}), content_type="application/json")
        return HttpResponse(serializers.serialize("json", [data]), content_type="application/json")
