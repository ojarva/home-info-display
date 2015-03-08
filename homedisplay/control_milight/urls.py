from django.conf.urls import patterns
from . import views

urlpatterns = patterns('',

    (r'^status$', views.Control.as_view()),
    (r'^status/(?P<group>([0-9]))$', views.Control.as_view()),
    (r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))$', views.Control.as_view()),
    (r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))/(?P<parameter>([0-9]+))$', views.Control.as_view()),
    (r'^control/source/(?P<source>([a-z_-]+))/(?P<command>([a-z_-]+))$', views.ControlPerSource.as_view()),
    (r'^timed/(?P<command>([a-z-_]+))/(?P<action>([a-z-_]+))$', views.TimedProgram.as_view()),
)
