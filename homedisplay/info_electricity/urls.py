from django.conf.urls import patterns
from . import views

urlpatterns = patterns('',
    (r'^get_json', views.get_json.as_view()),
    (r'^get_barchart_json', views.get_barchart_json.as_view()),
)
