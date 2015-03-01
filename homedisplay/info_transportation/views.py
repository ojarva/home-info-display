from .models import get_departures
from django.http import HttpResponse
from django.views.generic import View
import json

class get_json(View):
    """ Returns next departures per stop, only for currently active lines. """
    def get(self, request, *args, **kwargs):
        items = get_departures()
        return HttpResponse(json.dumps(items), content_type="application/json")
