from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, render_to_response
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import time


from .models import Task, TaskHistory

class info(View):
    def get(self, request, *args, **kwargs):
        todo_tasks = []
        for task in Task.objects.all():
            if task.last_completed_at is None:
                task.overdue = None
                todo_tasks.append(task)
                continue

            if task.overdue_by() > datetime.timedelta(0):
                task.overdue = task.overdue_by().total_seconds()
                todo_tasks.append(task)

        ret = []
        for item in todo_tasks:
            ret.append({"title": item.title, "overdue_by": item.overdue, "id": item.id })

        return render_to_response("repeating_tasks_content.html", {"data": ret}, RequestContext(request))

class done(View):
    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["task_id"])
        if task.time_since_completion() and task.time_since_completion() < datetime.timedelta(minutes=5):
            return HttpResponse("too_soon")
        task.completed()
        return HttpResponse("ok")
