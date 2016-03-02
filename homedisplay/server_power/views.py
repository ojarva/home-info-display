from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from homedisplay.utils import publish_ws
import json
import manage_server_power
import redis

redis_instance = redis.StrictRedis()

sp = manage_server_power.ServerPower(server_hostname=settings.SERVER_IP_ADDRESS, server_mac=settings.SERVER_MAC_ADDRESS,
                                     ssh_username=settings.SERVER_SSH_USERNAME, broadcast_ip=settings.SERVER_BROADCAST_IP)


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
        status["in_progress"] = redis_instance.get("server_power_in_progress")
        return HttpResponse(json.dumps(status), content_type="application/json")


class startup(View):

    def post(self, request, *args, **kwargs):
        status = sp.is_alive()
        sp.wake_up()
        redis_instance.setex("server_power_in_progress", 60, status)
        publish_ws("server_power", {"status": status, "in_progress": status})
        return HttpResponse("ok")


class shutdown(View):

    def post(self, request, *args, **kwargs):
        status = sp.is_alive()
        sp.shutdown()
        redis_instance.setex("server_power_in_progress", 60, status)
        publish_ws("server_power", {"status": status, "in_progress": status})
        return HttpResponse("ok")
