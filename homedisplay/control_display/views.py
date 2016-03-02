from .display_utils import run_display_command, cancel_delayed_shutdown
from .utils import initiate_delayed_shutdown
from django.http import HttpResponse
from django.views.generic import View
import redis
import subprocess

redis_instance = redis.StrictRedis()


class Power(View):

    def post(self, request, *args, **kwargs):

        cmd = kwargs.get("command")
        if cmd in ("off", "on"):
            # run_display_command automatically revokes possible delayed tasks
            run_display_command(cmd)
            return HttpResponse("ok")

        if cmd == "delayed-shutdown":
            initiate_delayed_shutdown()
            return HttpResponse("ok")
        elif cmd == "cancel-delayed":
            display_task = cancel_delayed_shutdown()
            if display_task:
                return HttpResponse("Revoked %s" % display_task)
            return HttpResponse("No task available")
        return HttpResponse("Invalid command")


class Brightness(View):

    def post(self, request, *args, **kwargs):
        set_destination_brightness(float(kwargs.get("brightness")))
        return HttpResponse("ok")


class RestartBrowser(View):

    def post(self, request, *args, **kwargs):
        p = subprocess.Popen(["killall", "chromium-browser"])
        p.wait()
        env = {"DISPLAY": ":0"}
        p = subprocess.Popen(["chromium-browser", "--touch-events=enabled", "--start-fullscreen",
                              "--disable-session-crashed-bubble", "--disable-touch-drag-drop", "--disable-pinch"], env=env, shell=True)
        p.wait()
        return HttpResponse("ok")
