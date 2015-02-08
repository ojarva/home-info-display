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
from .models import Electricity
from django.core import serializers


class get_json(View):
    def get(self, request, *args, **kwargs):
        time_start = now() - datetime.timedelta(days=70)
        items = []
        for item in Electricity.objects.filter(date__gte=time_start):
            d = {"timestamp": item.get_timestamp(), "value": {"W": float(item.usage)}}
            items.append(d)
        return HttpResponse(json.dumps(items), content_type="application/json")
