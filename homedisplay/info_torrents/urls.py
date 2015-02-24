from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^list$', views.List.as_view()),
    (r'^action/(?P<command>([a-z]+))/(?P<hash>([a-zA-Z0-9]+))', views.Action.as_view()),
)
