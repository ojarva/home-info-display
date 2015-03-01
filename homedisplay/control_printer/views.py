from .models import PrintLabel, get_serialized_labels
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth as reportlab_stringWidth
import cups
import datetime
import json
import redis

redis_instance = redis.StrictRedis()

#TODO: move to local_settings.py
CUPS_IP = "192.168.1.112"

class GetLabels(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(get_serialized_labels(), content_type="application/json")

class CancelJob(View):
    def post(self, request, *args, **kwargs):
        cups.setServer(CUPS_IP)
        cups_instance = cups.Connection()
        cups_instance.cancelJob(int(kwargs.get("job_id"))) # This does not return any useful information
        return HttpResponse("ok")

class GetPrinters(View):
    def get(self, request, *args, **kwargs):
        cups.setServer(CUPS_IP)
        cups_instance = cups.Connection()
        items = cups_instance.getPrinters()
        return HttpResponse(json.dumps(items), content_type="application/json")

class GetStatus(View):
    def get(self, request, *args, **kwargs):
        cups.setServer(CUPS_IP)
        cups_instance = cups.Connection()
        try:
            items = cups_instance.getJobs(requested_attributes=["job-id", "job-media-sheets-completed", "time-at-creation"])
        except:
            return HttpResponse("error")
        for key in items:
            items[key]["time-at-creation"] = datetime.datetime.fromtimestamp(items[key]["time-at-creation"]).isoformat()
        return HttpResponse(json.dumps(items), content_type="application/json")

class PrintLabels(View):
    def post(self, request, *args, **kwargs):
        c = canvas.Canvas("printjob.pdf",  pagesize=(260.787402, 108))
        c.showPage()
        c.save()
        return HttpResponse("ok")
