from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
import subprocess

def run_display_command(cmd):
    env = {"DISPLAY": ":0"}
    p = subprocess.Popen(["xset", "dpms", "force", cmd], env=env)
    p.wait()

class control_display(View):
    def get(self, request, *args, **kwargs):
        cmd = kwargs.get("command")
        if cmd == "off":
            run_display_command("off")
        elif cmd == "on":
            run_display_command("on")
        else:
            return HttpResponse("Invalid command")
        return HttpResponse("ok")
