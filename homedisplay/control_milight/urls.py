from django.conf.urls import patterns
from . import views

urlpatterns = patterns('',
    (r'^control/(?P<command>([a-z_-]+))/(?P<group>([0-9]))$', views.control.as_view()),
    (r'^control/source/(?P<source>([a-z_-]+))/(?P<command>([a-z_-]+))$', views.control_per_source.as_view()),

    (r'^timed/(?P<command>([a-z-_]+))/(?P<action>([a-z-_]+))$', views.timed.as_view()),
)
