from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View

class get_co2(View):
    def get(self, request, *args, **kwargs):
        co2 = open("/mnt/owfs/20.F1580D000000/CO2/ppm").read()
        temperature = open("/mnt/owfs/22.53B222000000/temperature").read()
        return HttpResponse(json.dumps({"co2": co2, "temperature": temperature}))
