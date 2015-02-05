from .models import Birthday
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import json
import time
import datetime

class list(View):
    def get(self, request, *args, **kwargs):
        if kwargs.get("date") == "all":
            items = Birthday.objects.all()
        else:
            date = now()
            if kwargs.get("date") == "tomorrow":
                date = date + datetime.timedelta(days=1)

            items = Birthday.objects.filter(birthday__month=date.month, birthday__day=date.day)
        return HttpResponse(serializers.serialize("json", items), content_type="application/json")
