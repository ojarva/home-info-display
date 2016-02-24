from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^status$', views.Status.as_view()),
    url(r'^control/(?P<command>(.*?))/(?P<arg>(.*))$', views.Control.as_view()),
    url(r'^control/(?P<command>(.*?))$', views.Control.as_view()),
]
