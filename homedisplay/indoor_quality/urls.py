from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get_modal$', views.get_modal.as_view()),
    (r'^get_keys$', views.get_keys.as_view()),
    (r'^get_json/(?P<sensor_id>([a-z0-9-_]+))$', views.get_json.as_view()),
    (r'^get_json/(?P<sensor_id>([a-z0-9-_]+))/trend$', views.get_json_trend.as_view()),
)
