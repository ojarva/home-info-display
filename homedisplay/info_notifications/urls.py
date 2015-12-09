from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    (r'^status$', views.NotificationsInfo.as_view()),
    (r'^dismiss/(?P<notification_id>[0-9]+)$', views.NotificationsInfo.as_view()),
    (r'^create$', views.NotificationUpdate.as_view()),
    (r'^delete/(?P<item_type>[A-Za-z-_]+)$', views.NotificationUpdate.as_view()),
)
