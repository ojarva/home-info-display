from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^status$', views.Control.as_view()),
    url(r'^status/(?P<group>([0-9]))$', views.Control.as_view()),
    url(r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))$', views.Control.as_view()),
    url(r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))/(?P<parameter>([0-9]+))$', views.Control.as_view()),
    url(r'^control/source/(?P<source>([a-z_-]+))/(?P<command>([a-z_-]+))$', views.ControlPerSource.as_view()),
    url(r'^timed/(?P<command>([a-z-_]+))/(?P<action>([a-z-_]+))$', views.TimedProgram.as_view()),
]
