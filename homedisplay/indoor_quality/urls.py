from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^co2$', views.get_co2.as_view()),
    (r'^co2/trend$', views.get_co2_trend.as_view()),
)
