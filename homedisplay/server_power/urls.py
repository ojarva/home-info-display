from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^status', views.info.as_view()),
    (r'^shutdown', views.shutdown.as_view()),
    (r'^startup', views.startup.as_view()),
)
