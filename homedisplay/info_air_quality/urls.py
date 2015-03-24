from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get/dialog/contents$', views.GetModalContent.as_view()),
    (r'^get/sensor/keys$', views.GetSensorKeys.as_view()),
    (r'^get/sensor/history/(?P<sensor_id>([a-z0-9-_]+))$', views.GetHistoryForSensor.as_view()),
    (r'^get/sensor/(?P<sensor_id>([a-z0-9-_]+))/trend$', views.GetTrendForSensor.as_view()),
    (r'^get/sensor/(?P<sensor_id>([a-z0-9-_]+))/latest$', views.GetLatestSensorReadings.as_view()),
    (r'^get/outdoor/latest', views.GetLatestOutdoor.as_view()),
)
