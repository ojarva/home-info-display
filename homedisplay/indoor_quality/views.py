from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.core import serializers

from .models import IndoorQuality

class get_co2(View):
    def get(self, request, *args, **kwargs):
        data = IndoorQuality.objects.all()[0:]
        co2 = open("/mnt/owfs/20.F1580D000000/CO2/ppm").read()
        temperature = open("/mnt/owfs/22.53B222000000/temperature").read()
        data = {"co2": co2, "temperature": temperature}
        return HttpResponse(serializers.serialize("json", data), content_type="application/json")
