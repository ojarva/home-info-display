from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^status$', views.NotificationsInfo.as_view()),
    url(r'^dismiss/(?P<notification_id>[0-9]+)$', views.NotificationsInfo.as_view()),
    url(r'^create$', views.NotificationUpdate.as_view()),
    url(r'^delete/(?P<item_type>[A-Za-z-_]+)$', views.NotificationUpdate.as_view()),
]
