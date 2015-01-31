from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^', include('homedisplay.urls_base')),
    url(r'^homecontroller/', include('homedisplay.urls_base')),
)
