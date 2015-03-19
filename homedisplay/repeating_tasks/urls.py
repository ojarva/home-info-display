from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get_json/(?P<date>([a-z_-]+))$', views.GetJson.as_view()),
    (r'^snooze/(?P<task_id>([0-9]+))/(?P<days>([0-9-]+))', views.Snooze.as_view()),
    (r'^done/(?P<task_id>([0-9]+))', views.Done.as_view()),
)
