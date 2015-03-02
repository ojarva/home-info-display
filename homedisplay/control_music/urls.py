from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^control/(?P<command>([a-z]+))$', views.PlayControl.as_view()),
    url(r'^status/position', views.PlayPosition.as_view()),
    url(r'^status/state', views.PlayState.as_view()),
    url(r'^queue/add', views.Queue.as_view()),
)
