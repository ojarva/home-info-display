from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^power/(?P<command>([a-z]+))$', views.Power.as_view()),
    (r'^brightness/(?P<brightness>([0-9]*))', views.Brightness.as_view()),
    (r'^restart$', views.RestartBrowser.as_view()),
)
