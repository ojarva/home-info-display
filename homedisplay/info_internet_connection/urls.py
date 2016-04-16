from django.conf.urls import url
from . import views

urlpatterns = [  # pylint:disable=invalid-name
    url(r'^status', views.GetJson.as_view()),
    url(r'^wifi/info', views.WifiInfo.as_view()),
]
