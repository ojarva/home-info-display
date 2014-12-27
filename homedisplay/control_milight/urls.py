from django.conf.urls import patterns
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^content', TemplateView.as_view(template_name="lightcontrol.html")),
    (r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))', views.control.as_view()),
)
