from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^power/(?P<command>([a-z-]+))$', views.Power.as_view()),
    url(r'^brightness/(?P<brightness>([0-9]*))', views.Brightness.as_view()),
    url(r'^restart$', views.RestartBrowser.as_view()),
]
