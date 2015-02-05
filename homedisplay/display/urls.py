from django.conf.urls import patterns
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^content$', TemplateView.as_view(template_name="index.html")),
    (r'^content/kitchen', TemplateView.as_view(template_name='index_kitchen.html')),
    (r'^content/door', TemplateView.as_view(template_name='index_door.html')),
)
