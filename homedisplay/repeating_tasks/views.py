from .models import Task, get_repeating_data
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
import datetime
import json


class GetJson(View):

    def get(self, request, *args, **kwargs):
        date = kwargs.get("date")
        todo_tasks = get_repeating_data(date)
        return HttpResponse(json.dumps(todo_tasks), content_type="application/json")


class Snooze(View):

    def patch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["task_id"])
        days = int(kwargs["days"])
        if days < 0:
            task.show_immediately = True
            task.snooze = None
            task.save()
        else:
            task.snooze_by(days)
        return HttpResponse("ok")


class Done(View):

    def patch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["task_id"])
        if task.time_since_completion() and task.time_since_completion() < datetime.timedelta(minutes=5):
            return HttpResponse("too_soon")
        task.completed()
        return HttpResponse("ok")
