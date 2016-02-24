from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^current_time$', views.CurrentTime.as_view()),
    url(r'^list$', views.List.as_view()),
    url(r'^create$', views.Create.as_view()),
    url(r'^get/(?P<id>([0-9]+))$', views.Get.as_view()),
    url(r'^stop/(?P<id>([0-9]+))$', views.Stop.as_view()),
    url(r'^start/(?P<id>([0-9]+))$', views.Start.as_view()),
    url(r'^restart/(?P<id>([0-9]+))$', views.Restart.as_view()),
    url(r'^delete/(?P<id>([0-9]+))$', views.Delete.as_view()),
    url(r'^get_labels$', views.GetLabels.as_view()),
]
