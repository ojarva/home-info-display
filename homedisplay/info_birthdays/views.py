from .models import Birthday, get_birthdays
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
        return HttpResponse(json.dumps(get_birthdays(kwargs.get("date"))), content_type="application/json")
