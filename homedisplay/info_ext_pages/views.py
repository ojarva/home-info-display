from .models import ExtPage
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View
from homedisplay.utils import publish_ws
import json


class PushExt(View):

    def post(self, request, *args, **kwargs):
        url = request.POST.get("page")
        if url is None or len(url) < 3:
            raise HttpResponseBadRequest

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://%s" % url

        should_add = True
        try:
            a = ExtPage.objects.latest()
            if a.url == url:
                should_add = False
        except ExtPage.DoesNotExist:
            pass

        if should_add:
            a = ExtPage(url=url)
            a.save()

        publish_ws("open-ext-page", {"url": url, "id": a.pk})
        return HttpResponse("ok")

    def get(self, request, *args, **kwargs):
        if kwargs.get("latest"):
            try:
                a = ExtPage.objects.latest()
                return HttpResponse(json.dumps({"url": a.url, "id": a.pk}), content_type="application/json")
            except ExtPage.DoesNotExist:
                raise Http404

        direction = kwargs.get("direction")
        if direction:
            # This assumes primary keys are sortable, and monotonously growing.
            data = {"url": "", "id": None}
            id = int(kwargs.get("id"))
            q = None
            if direction == "after":
                q = ExtPage.objects.order_by("pk").filter(pk__gt=id)
            elif direction == "before":
                q = ExtPage.objects.order_by("-pk").filter(pk__lt=id)
            if q is None:
                raise Http404

            if len(q) > 0:
                q = q[0]
                data["url"] = q.url
                data["id"] = q.pk
            return HttpResponse(json.dumps(data), content_type="application/json")
        # By default, return 50 latest urls
        return HttpResponse(serializers.serialize("json", ExtPage.objects.all()[0:50]), content_type="application/json")
