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

class info(View):
    def get(self, request, *args, **kwargs):
        todo_tasks = []
        date = kwargs.get("date")
        for task in Task.objects.all():
            if date == "today":
                if task.last_completed_at is None:
                    todo_tasks.append(task)
                    continue

                if task.overdue_by() > datetime.timedelta(0):
                    todo_tasks.append(task)
            elif date == "tomorrow":
                if task.last_completed_at is None:
                    continue

                overdue_by = task.overdue_by()
                if overdue_by > datetime.timedelta(days=-1) and overdue_by < datetime.timedelta(0):
                    todo_tasks.append(task)

        return HttpResponse(serializers.serialize("json", todo_tasks), content_type="application/json")

class done(View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["task_id"])
        if task.time_since_completion() and task.time_since_completion() < datetime.timedelta(minutes=5):
            return HttpResponse("too_soon")
        task.completed()
        return HttpResponse("ok")
