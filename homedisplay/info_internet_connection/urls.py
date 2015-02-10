from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^status', views.get_json.as_view()),
)
