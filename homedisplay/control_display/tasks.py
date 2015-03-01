from __future__ import absolute_import
from celery import shared_task
from .display_utils import run_display_command
import redis

__all__ = ["run_display_command_task"]

@shared_task
def run_display_command_task():
    redis_instance = redis.StrictRedis()
    command = redis_instance.get("display-control-command")
    if command is None:
        return "Command is no longer available - task is revoked"
    redis_instance.delete("display-control-command")
    redis_instance.delete("display-control-task")
    run_display_command(command)
    return "Executed %s" % command
