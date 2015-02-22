from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import now
from django.views.generic import View
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth as reportlab_stringWidth
import cups
import datetime
import json
import redis
import reportlab
import time

redis_instance = redis.StrictRedis()

CUPS_IP = "192.168.1.112"

class cancel_job(View):
    def post(self, request, *args, **kwargs):
        cups.setServer(CUPS_IP)
        cups_instance = cups.Connection()
        cups_instance.cancelJob(int(kwargs.get("job_id"))) # This does not return any useful information
        return HttpResponse("ok")

class get_printers(View):
    def get(self, request, *args, **kwargs):
        cups.setServer(CUPS_IP)
        cups_instance = cups.Connection()
        items = cups_instance.getPrinters()
        return HttpResponse(json.dumps(items), content_type="application/json")

class get_status(View):
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

class print_label(View):
    def post(self, request, *args, **kwargs):
        c = canvas.Canvas("printjob.pdf",  pagesize=(260.787402, 108))
        c.showPage()
        c.save()
        return HttpResponse("ok")
