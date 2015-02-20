from .models import Weather
from astral import Astral
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import subprocess
import time

def calculate_apparent_temperature(temperature, wind, humidity):
    wind /= 3.6
    windchill = (13.12 + 0.6215 * temperature - 11.37 * (wind ** 0.16) + 0.3965 * temperature * (wind ** 0.16))
    href = 0.2

    simmer = (1.8 * temperature - 0.55 * (1 - humidity / 100) * (1.8 * temperature - 26) - 0.55 * (1 - href) * 26) / (1.8 * (1 - 0.55 * (1 - href)))
    return round(min(windchill, simmer))

def get_wind_readable(wind):
    wind /= 3.6
    if wind < 0.2:
        return "tyyni"
    elif wind < 3.3:
        return "heikko"
    elif wind < 7.9:
        return "kohtaleinen"
    elif wind < 13.8:
        return "navakka"
    elif wind < 20.7:
        return "kova"
    else:
        return "myrsky"

def get_weather_data():
    time_now = now()
    forecast = {"hours": json.loads(serializers.serialize("json", Weather.objects.filter(date__gte=time_now.date())))}
    for item in forecast["hours"]:
        item["fields"]["apparent_temperature"] = calculate_apparent_temperature(item["fields"]["temperature"], float(item["fields"]["wind_speed"]), item["fields"]["humidity"])
        item["fields"]["wind_speed_readable"] = get_wind_readable(float(item["fields"]["wind_speed"]))

    sun_info = Astral()
    sun_info.solar_depression = 'civil'
    b = sun_info[settings.SUN_CITY].sun()
    for k in b:
        b[k] = unicode(b[k])
    forecast["sun"] = b
    return forecast


class get_json(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(get_weather_data()), content_type="application/json")
