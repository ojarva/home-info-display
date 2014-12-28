from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = patterns('',
    (r'^content', TemplateView.as_view(template_name="internet_connection.html")),
    (r'^status', views.info.as_view()),
)
