from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get_json/(?P<date>([a-z_-]+))$', views.get_json.as_view()),
    (r'^snooze/(?P<task_id>([0-9]+))/(?P<days>([0-9-]+))', views.snooze.as_view()),
    (r'^done/(?P<task_id>([0-9]+))', views.done.as_view()),
)
