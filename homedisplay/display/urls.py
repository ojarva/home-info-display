from django.conf.urls import patterns
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^content', TemplateView.as_view(template_name="index.html")),
)
