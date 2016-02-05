from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^status$', views.Status.as_view()),
    (r'^control/(?P<command>(.*?))/(?P<arg>(.*))$', views.Control.as_view()),
    (r'^control/(?P<command>(.*?))$', views.Control.as_view()),
)
