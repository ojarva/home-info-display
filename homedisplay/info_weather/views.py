# -*- coding: utf-8 -*-

from django.conf import settings
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
import datetime
import json
import redis

redis_instance = redis.StrictRedis()


class get_json(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(redis_instance.get("weather-all"), content_type="application/json")
