from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View
from homedisplay.utils import publish_ws

class Wrapped(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("index_frame.html", {"frame_src": "/homecontroller/display/content/%s" % kwargs.get("view") }, context_instance=RequestContext(request))

class PushExt(View):
    def post(self, request, *args, **kwargs):
        publish_ws("open-ext-page", request.POST.get("page"))
        return HttpResponse("ok")
