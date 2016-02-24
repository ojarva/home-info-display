from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^status', views.info.as_view()),
    url(r'^shutdown', views.shutdown.as_view()),
    url(r'^startup', views.startup.as_view()),
]
