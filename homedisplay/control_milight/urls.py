from django.conf.urls import patterns
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))', views.control.as_view()),
    (r'^control/source/(?P<source>([a-z_-]+))/(?P<command>([a-z_-]+))', views.control_per_source.as_view()),
)
