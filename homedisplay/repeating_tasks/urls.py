from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^content', TemplateView.as_view(template_name="repeating_tasks.html")),
    (r'^status', views.info.as_view()),
    (r'^done/(?P<task_id>([0-9]+))', views.done.as_view()),
)
