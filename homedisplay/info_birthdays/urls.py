from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    (r'^get_json/(?P<date>([a-z_-]+))$', views.list.as_view()),
)
