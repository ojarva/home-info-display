from .models import *
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import redis
import time

redis_instance = redis.StrictRedis()

class get_json(View):
    def get(self, request, *args, **kwargs):
        items = get_departures()
        return HttpResponse(json.dumps(items), content_type="application/json")
