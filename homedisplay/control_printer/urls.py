from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^get_labels$', views.GetLabels.as_view()),
    url(r'^cancel_job/(?P<job_id>([0-9]+))$', views.CancelJob.as_view()),
    url(r'^get_status$', views.GetStatus.as_view()),
    url(r'^get_printers$', views.GetPrinters.as_view()),
    url(r'^print_label$', views.PrintLabels.as_view()),
]
