from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('homedisplay.urls_base')),
    url(r'^homecontroller/', include('homedisplay.urls_base')),
]
