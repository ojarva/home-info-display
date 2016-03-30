from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list$', views.list.as_view()),
    url(r'^get/(?P<id>([a-z0-9_-]+))$', views.item.as_view()),
    url(r'^item/(?P<id>([:a-z0-9_-]+))$', views.get_or_create.as_view()),
]
