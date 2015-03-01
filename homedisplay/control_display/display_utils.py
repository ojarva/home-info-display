import redis
import json
import subprocess
import logging
from homedisplay.celery import app as celery_app

logger = logging.getLogger(__name__)
redis_instance = redis.StrictRedis()


def cancel_delayed_shutdown():
    display_task = redis_instance.get("display-control-task")
    redis_instance.delete("display-control-command")
    if display_task:
        celery_app.control.revoke(display_task)
        redis_instance.delete("display-control-task")
        return display_task
    redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": "cancel-delayed"}))
    return False

def run_display_command(cmd):
    env = {"DISPLAY": ":0"}
    logger.info("Running display command %s", cmd)
    p = subprocess.Popen(["xset", "dpms", "force", cmd], env=env)
    content = None
    if cmd == "off":
        content = "display-off"
    elif cmd == "on":
        content = "display-on"
    p.wait()
    if content:
        cancel_delayed_shutdown()
        redis_instance.publish("home:broadcast:generic", json.dumps({"key": "shutdown", "content": content}))
