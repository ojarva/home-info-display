from .models import Notification
from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import json
import redis

redis_instance = redis.StrictRedis()

class NotificationsInfo(View):
    """ API for display """
    def get(self, request, *args, **kwargs):
        return HttpResponse(serializers.serialize("json", Notification.objects.all()), content_type="application/json")

    @method_decorator(csrf_exempt)
    def delete(self, request, *args, **kwargs):
        obj = Notification.objects.get(id=kwargs.get("notification_id"))
        item_type = obj.item_type
        obj.delete()
        redis_instance.publish("%s-pubsub" % item_type, json.dumps({"action": "user_dismissed"}))
        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

class NotificationUpdate(View):
    """ API for backend components """
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        try:
            item = Notification.objects.get(item_type=request.POST.get("item_type"))
        except Notification.DoesNotExist:
            item = Notification()
            item.item_type = request.POST.get("item_type")
        item.description = request.POST.get("description")
        item.can_dismiss = request.POST.get("can_dismiss") in ["1", "True", "true"]

        item.save()
        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")

    @method_decorator(csrf_exempt)
    def delete(self, request, *args, **kwargs):
        Notification.objects.filter(item_type=kwargs.get("item_type")).delete()
        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
