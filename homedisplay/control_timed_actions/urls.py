from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^current_time$', views.current_time.as_view()),

    (r'^list$', views.list.as_view()),
    (r'^create$', views.create.as_view()),
    (r'^get/(?P<id>([0-9]+))$', views.get.as_view()),
    (r'^stop/(?P<id>([0-9]+))$', views.stop.as_view()),
    (r'^start/(?P<id>([0-9]+))$', views.start.as_view()),
    (r'^restart/(?P<id>([0-9]+))$', views.restart.as_view()),
    (r'^delete/(?P<id>([0-9]+))$', views.delete.as_view()),
)
