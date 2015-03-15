from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^push/page$', views.PushExt.as_view()),
    url(r'^pull/pages$', views.PushExt.as_view()),
    url(r'^pull/page/before/(?P<id>([0-9]+))', views.PushExt.as_view(), {"direction": "before"}),
    url(r'^pull/page/after/(?P<id>([0-9]+))', views.PushExt.as_view(), {"direction": "after"}),
    url(r'^pull/page/latest', views.PushExt.as_view(), {"latest": True}),

)
