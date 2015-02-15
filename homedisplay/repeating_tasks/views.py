from .models import Task, TaskHistory
from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import time

from .models import get_repeating_data

class get_json(View):
    def get(self, request, *args, **kwargs):
        date = kwargs.get("date")
        todo_tasks = get_repeating_data(date)
        return HttpResponse(serializers.serialize("json", todo_tasks), content_type="application/json")

class snooze(View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["task_id"])
        days = int(kwargs["days"])
        task.snooze_by(days)
        return HttpResponse("ok")

class done(View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["task_id"])
        if task.time_since_completion() and task.time_since_completion() < datetime.timedelta(minutes=5):
            return HttpResponse("too_soon")
        task.completed()
        return HttpResponse("ok")
