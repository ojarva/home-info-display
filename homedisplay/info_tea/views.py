from .models import NfcTag
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.core import urlresolvers
from django.utils import timezone
from django.views.generic import View
import json


class list(View):

    def get(self, request, *args, **kwargs):
        items = NfcTag.objects.all()
        return HttpResponse(serializers.serialize("json", items), content_type="application/json")


class item(View):
    def get(self, request, *args, **kwargs):
        item = NfcTag.objects.get(tag_id=kwargs["id"])
        serialized = json.loads(serializers.serialize("json", [item]))
        return HttpResponse(json.dumps(serialized[0]), content_type="application/json")

    def post(self, request, *args, **kwargs):
        item = NfcTag.objects.get(tag_id=kwargs["id"])
        if item.first_used_at is None:
            item.first_used_at = timezone.now()
        item.last_used_at = timezone.now()
        item.save()
        serialized = json.loads(serializers.serialize("json", [item]))
        return HttpResponse(json.dumps(serialized[0]), content_type="application/json")


class get_or_create(View):
    def get(self, request, *args, **kwargs):
        try:
            item = NfcTag.objects.get(tag_id=kwargs["id"])
            return HttpResponseRedirect(urlresolvers.reverse("admin:info_tea_nfctag_change", args=(item.id,)))
        except NfcTag.DoesNotExist:
            item = NfcTag(tag_id=kwargs["id"], name="Auto")
            item.save()
        return HttpResponseRedirect(urlresolvers.reverse("admin:info_tea_nfctag_change", args=(item.id,)))
