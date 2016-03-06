from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^fridge$', views.Fridge.as_view()),
    url(r'^door$', views.Door.as_view()),
]
