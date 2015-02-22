from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^cancel_job/(?P<job_id>([0-9]+))$', views.cancel_job.as_view()),
    (r'^get_status$', views.get_status.as_view()),
    (r'^get_printers$', views.get_printers.as_view()),

    (r'^print_label$', views.print_label.as_view()),
)
