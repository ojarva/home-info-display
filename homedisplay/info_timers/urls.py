from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^content$', TemplateView.as_view(template_name="timers.html")),

    (r'^current_time$', views.current_time.as_view()),

    (r'^timer/list$', views.list.as_view()),
    (r'^timer/create$', views.create.as_view()),
    (r'^timer/get/(?P<id>([0-9]+))$', views.get.as_view()),
    (r'^timer/stop/(?P<id>([0-9]+))$', views.stop.as_view()),
    (r'^timer/start/(?P<id>([0-9]+))$', views.start.as_view()),
    (r'^timer/restart/(?P<id>([0-9]+))$', views.restart.as_view()),
    (r'^timer/delete/(?P<id>([0-9]+))$', views.delete.as_view()),
)
