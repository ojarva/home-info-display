from django.conf.urls import patterns
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
    (r'^content$', TemplateView.as_view(template_name="index.html")),
    (r'^content/kitchen', TemplateView.as_view(template_name='index_kitchen.html')),
    (r'^content/door', TemplateView.as_view(template_name='index_door.html')),
    (r'^content/computer', TemplateView.as_view(template_name='index_computer.html')),
    (r'^control/(?P<command>([a-z]+))$', views.control_display.as_view()),

)
