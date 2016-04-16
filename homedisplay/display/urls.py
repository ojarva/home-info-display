from django.conf.urls import url
from django.views.generic import TemplateView

import views

urlpatterns = [  # pylint:disable=invalid-name
    url(r'^content/display$', TemplateView.as_view(template_name="main/display.html")),
    url(r'^content/kitchen$', TemplateView.as_view(template_name='main/kitchen.html')),
    url(r'^content/door$', TemplateView.as_view(template_name='main/door.html')),
    url(r'^content/computer$', TemplateView.as_view(template_name='main/computer.html')),

    url(r'^content/wrapped/(?P<view>([a-zA-Z0-9-_]+))$',
        views.Wrapped.as_view()),
]
