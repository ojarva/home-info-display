from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^fridge$', views.Fridge.as_view()),
)
