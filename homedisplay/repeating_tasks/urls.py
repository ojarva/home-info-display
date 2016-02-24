from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^get_json/(?P<date>([a-z_-]+))$', views.GetJson.as_view()),
    url(r'^snooze/(?P<task_id>([0-9]+))/(?P<days>([0-9-]+))', views.Snooze.as_view()),
    url(r'^done/(?P<task_id>([0-9]+))', views.Done.as_view()),
]
