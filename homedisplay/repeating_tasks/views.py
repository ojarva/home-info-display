from .models import Task, get_repeating_data
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
import datetime

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
