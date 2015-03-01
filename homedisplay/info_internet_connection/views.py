from .models import get_latest_serialized
from django.core import serializers
from django.http import HttpResponse
from django.views.generic import View
import json

class get_json(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(get_latest_serialized()), content_type="application/json")
