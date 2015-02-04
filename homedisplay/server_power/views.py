from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import manage_server_power
import subprocess
import time

sp = manage_server_power.ServerPower(server_hostname=settings.SERVER_IP_ADDRESS, server_mac=settings.SERVER_MAC_ADDRESS, ssh_username=settings.SERVER_SSH_USERNAME, broadcast_ip=settings.SERVER_BROADCAST_IP)

class info(View):
    def get(self, request, *args, **kwargs):
        status = {"status": "unknown"}
        alive_status = sp.is_alive()
        if alive_status == manage_server_power.SERVER_UP:
            status["status"] = "running"
        elif alive_status == manage_server_power.SERVER_UP_NOT_RESPONDING:
            status["status"] = "not_responding"
        elif alive_status == manage_server_power.SERVER_DOWN:
            status["status"] = "down"

        return HttpResponse(json.dumps(status), content_type="application/json")


class startup(View):
    def get(self, request, *args, **kwargs):
        sp.wake_up()
        return HttpResponse("ok")


class shutdown(View):
    def get(self, request, *args, **kwargs):
        sp.shutdown()
        return HttpResponse("ok")
