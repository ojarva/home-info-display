from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get/dialog/contents$', views.GetModalContent.as_view()),
    (r'^get/sensor/(?P<sensor_id>([a-z0-9-_]+))/history$', views.GetHistoryForSensor.as_view()),
    (r'^get/sensor/(?P<sensor_id>([a-z0-9-_]+))/latest$', views.GetLatestSensorReadings.as_view()),
    (r'^get/outdoor/latest', views.GetLatestOutdoor.as_view()),
)
