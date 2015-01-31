from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import subprocess
import time
from .models import Weather
from django.core import serializers


class get_json(View):
    def get(self, request, *args, **kwargs):
        time_now = now()
        forecast = (Weather.objects.filter(date__gte=time_now.date()))
        return HttpResponse(serializers.serialize("json", forecast), content_type="application/json")
