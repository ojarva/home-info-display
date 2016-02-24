from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^get_json$', views.GetJson.as_view()),
    url(r'^data/(?P<url>.*)', views.GetData.as_view()),
    url(r'^poikkeustiedotteet', views.Poikkeustiedotteet.as_view()),
]
