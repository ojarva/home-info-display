from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^get_json/(?P<date>([a-z_-]+))$', views.info.as_view()),
    (r'^done/(?P<task_id>([0-9]+))', views.done.as_view()),
)
