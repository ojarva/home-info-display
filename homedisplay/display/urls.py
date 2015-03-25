from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
    (r'^content/display$', TemplateView.as_view(template_name="main/display.html")),
    (r'^content/kitchen$', TemplateView.as_view(template_name='main/kitchen.html')),
    (r'^content/door$', TemplateView.as_view(template_name='main/door.html')),
    (r'^content/computer$', TemplateView.as_view(template_name='main/computer.html')),

    url(r'^content/wrapped/(?P<view>([a-zA-Z0-9-_]+))$', views.Wrapped.as_view()),
)
