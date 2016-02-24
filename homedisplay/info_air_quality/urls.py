from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^get/dialog/contents$', views.GetModalContent.as_view()),
    url(r'^get/sensor/(?P<sensor_id>([a-z0-9-_]+))/history$', views.GetHistoryForSensor.as_view()),
    url(r'^get/sensor/(?P<sensor_id>([a-z0-9-_]+))/latest$', views.GetLatestSensorReadings.as_view()),
    url(r'^get/outdoor/latest', views.GetLatestOutdoor.as_view()),
]
