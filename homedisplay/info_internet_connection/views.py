from .models import get_latest_serialized
from django.core import serializers
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
import json


class GetJson(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(get_latest_serialized()), content_type="application/json")


class WifiInfo(View):

    def get(self, request, *args, **kwargs):
        wifi_settings = {
            "ssid": settings.WIFI_SSID,
            "passphrase": settings.WIFI_PASSPHRASE
        }
        return HttpResponse(json.dumps(wifi_settings), content_type="application/json")
