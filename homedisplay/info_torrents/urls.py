from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list$', views.List.as_view()),
    url(r'^action/(?P<command>([a-z]+))/(?P<hash>([a-zA-Z0-9]+))', views.Action.as_view()),
]
