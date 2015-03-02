import redis
import json
import subprocess
import logging
from homedisplay.celery import app as celery_app
from homedisplay.utils import publish_ws

logger = logging.getLogger(__name__)
redis_instance = redis.StrictRedis()

__all__ = ["cancel_delayed_shutdown", "run_display_command"]

def cancel_delayed_shutdown():
    """ Cancels delayed shutdown, if one is running """
    display_task = redis_instance.get("display-control-task")
    redis_instance.delete("display-control-command")
    publish_ws("shutdown", "cancel-delayed")
    if display_task:
        celery_app.control.revoke(display_task)
        redis_instance.delete("display-control-task")
        logger.info("cancel_delayed_shutdown revoked %s", display_task)
        return display_task
    logger.info("cancel_delayed_shutdown did not find task to be revoked")
    return False

def run_display_command(cmd):
    """ Runs xset command. This method does not validate command, but it is escaped properly. """
    env = {"DISPLAY": ":0"}
    logger.info("Running display command %s", cmd)
    process = subprocess.Popen(["xset", "dpms", "force", cmd], env=env)
    content = None
    if cmd == "off":
        content = "display-off"
    elif cmd == "on":
        content = "display-on"
    process.wait()
    if content:
        cancel_delayed_shutdown()
        logger.info("Broadcasting display status: %s", content)
        publish_ws("shutdown", content)
