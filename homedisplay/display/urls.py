from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
    (r'^content/display$', TemplateView.as_view(template_name="index_display.html")),
    (r'^content/kitchen$', TemplateView.as_view(template_name='index_kitchen.html')),
    (r'^content/door$', TemplateView.as_view(template_name='index_door.html')),
    (r'^content/computer$', TemplateView.as_view(template_name='index_computer.html')),

    url(r'^content/wrapped/(?P<view>([a-zA-Z0-9-_]+))$', views.Wrapped.as_view()),
)
