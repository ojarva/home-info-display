from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_json/(?P<date>([a-z_-]+))$', views.list.as_view()),
]
