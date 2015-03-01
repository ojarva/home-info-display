from .models import Electricity
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View
import datetime
import json


class get_json(View):
    """ Returns list of timestamp-consumption pairs. """
    def get(self, request, *args, **kwargs):
        time_start = timezone.now() - datetime.timedelta(days=83)
        items = []
        for item in Electricity.objects.filter(date__gte=time_start):
            d = {"timestamp": item.get_timestamp(), "value": {"W": float(item.usage)}}
            items.append(d)
        return HttpResponse(json.dumps(items), content_type="application/json")


class get_barchart_json(View):
    """ Returns zero-filled list of timestamp-consumption pairs. """
    def get(self, request, *args, **kwargs):
        time_start = timezone.now() - datetime.timedelta(days=83)
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
        if current_date and consumption:
            items.append({"date": current_date.isoformat(), "consumption": consumption})

        return HttpResponse(json.dumps(items), content_type="application/json")
