from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^status', views.GetJson.as_view()),
    (r'^wifi/info', views.WifiInfo.as_view()),
)
