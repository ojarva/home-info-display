from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View
from homedisplay.utils import publish_ws


class Wrapped(View):

    # celery breaks if there's two arguments with same name
    def get(self, a, *b, **kwargs):  # pylint:disable=no-self-use
        return render_to_response("main/frame.html", {"frame_src": "/homecontroller/display/content/%s" % kwargs.get("view")}, context_instance=RequestContext(request))
