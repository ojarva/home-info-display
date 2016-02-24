from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^get_json$', views.get_json.as_view()),
]
