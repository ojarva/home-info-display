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


class get_json(View):
    def get(self, request, *args, **kwargs):
        todo_tasks = []
        date = kwargs.get("date")
        tasks = Task.objects.all()
        tasks = sorted(tasks, key=lambda t: t.overdue_by())
        tasks.reverse()
        if date == "today":
            day_starts = now().replace(hour=0, minute=0, second=0)
            day_ends = now().replace(hour=23, minute=59, second=59)
        elif date == "tomorrow":
            day_starts = now().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
            day_ends = now().replace(hour=23, minute=59, second=59) + datetime.timedelta(days=1)
        else:
            day_starts = day_ends = None
        print day_starts, day_ends
        for task in tasks:
            exp_at = task.expires_at()
            if day_starts and day_ends:
                if day_starts < exp_at and day_ends > exp_at:
                    todo_tasks.append(task)
            elif date == "all":
                todo_tasks.append(task)
        todo_tasks = sorted(todo_tasks, key=lambda t: t.optional)
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
