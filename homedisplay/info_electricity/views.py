from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import subprocess
import time
from .models import Electricity
from django.core import serializers


class get_json(View):
    def get(self, request, *args, **kwargs):
        time_start = now() - datetime.timedelta(days=83)
        items = []
        for item in Electricity.objects.filter(date__gte=time_start):
            d = {"timestamp": item.get_timestamp(), "value": {"W": float(item.usage)}}
            items.append(d)
        return HttpResponse(json.dumps(items), content_type="application/json")

class get_barchart_json(View):
    def get(self, request, *args, **kwargs):
        time_start = now() - datetime.timedelta(days=83)
        items = []
        current_date = None
        consumption = 0
        db_items = Electricity.objects.filter(date__gte=time_start)
        start_date = db_items[0].date

        for item in db_items:
            if current_date is None:
                current_date = item.date
            else:
                if current_date != item.date:
                    # Day changed
                    items.append({"date": current_date.isoformat(), "consumption": consumption})
                    consumption = 0
                    if item.date != current_date + datetime.timedelta(days=1):
                        # Skipping days
                        fill_day = current_date + datetime.timedelta(days=1)
                        while item.date != fill_day:
                            items.append({"date": fill_day.isoformat(), "consumption": 0})
                            fill_day += datetime.timedelta(days=1)
                    current_date = item.date
            consumption += float(item.usage)

        return HttpResponse(json.dumps(items), content_type="application/json")
