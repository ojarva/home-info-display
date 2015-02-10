from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get_json/(?P<sensor_id>(.+)$', views.get_json.as_view()),
    (r'^get_json/(?P<sensor_id>(.+)/trend$', views.get_json_trend.as_view()),
)
