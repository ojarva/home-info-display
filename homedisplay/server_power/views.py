from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Template
from django.utils.timezone import now
from django.views.generic import View
import datetime
import json
import subprocess
import time
import manage_server_power

class info(View):
    def get(self, request, *args, **kwargs):
        ping_response = subprocess.Popen(["/sbin/ping", "-c1", "-W 100", settings.SERVER_IP_ADDRESS], stdout=subprocess.PIPE)
        ping_response.communicate()
        ret = {"ping": False}
        print ping_response.returncode
        if ping_response.returncode == 0:
            ret["ping"] = True
        return render_to_response("server_power_content.html", ret, RequestContext(request))

class startup(View):
    def get(self, request, *args, **kwargs):
        wol.send_magic_packet(settings.SERVER_MAC_ADDRESS, ip_address="192.168.1.255")
        return HttpResponse("ok")


class shutdown(View):
    def get(self, request, *args, **kwargs):

        return HttpResponse("ok")
