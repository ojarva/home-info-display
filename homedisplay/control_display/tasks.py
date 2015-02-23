from __future__ import absolute_import
from celery import shared_task
from control_display.utils import run_display_command
import redis
import json

@shared_task
def run_display_command():
    redis_instance = redis.StrictRedis()
    command = redis_instance.get("display-control-command")
    if command not None:
        return
    command = json.loads(command)
    run_display_command(command["execute"])
    return "Executed %s" % command
