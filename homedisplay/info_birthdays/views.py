from .models import get_birthdays
from django.http import HttpResponse
from django.views.generic import View
import json


class list(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps(get_birthdays(kwargs.get("date"))), content_type="application/json")
