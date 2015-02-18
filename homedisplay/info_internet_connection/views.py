from .models import Internet, get_latest_serialized
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import View
import json
import time
class get_json(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(get_latest_serialized()), content_type="application/json")
