from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^get_labels$', views.GetLabels.as_view()),
    (r'^cancel_job/(?P<job_id>([0-9]+))$', views.CancelJob.as_view()),
    (r'^get_status$', views.GetStatus.as_view()),
    (r'^get_printers$', views.GetPrinters.as_view()),

    (r'^print_label$', views.PrintLabels.as_view()),
)
