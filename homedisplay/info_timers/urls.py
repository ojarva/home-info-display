from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^current_time$', views.CurrentTime.as_view()),

    (r'^list$', views.List.as_view()),
    (r'^create$', views.Create.as_view()),
    (r'^get/(?P<id>([0-9]+))$', views.Get.as_view()),
    (r'^stop/(?P<id>([0-9]+))$', views.Stop.as_view()),
    (r'^start/(?P<id>([0-9]+))$', views.Start.as_view()),
    (r'^restart/(?P<id>([0-9]+))$', views.Restart.as_view()),
    (r'^delete/(?P<id>([0-9]+))$', views.Delete.as_view()),

    (r'^get_labels$', views.GetLabels.as_view()),
)
