from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.core import serializers

from .models import IndoorQuality

class get_co2(View):
    def get(self, request, *args, **kwargs):
        data = IndoorQuality.objects.all()[0:1440]
        return HttpResponse(serializers.serialize("json", data), content_type="application/json")
