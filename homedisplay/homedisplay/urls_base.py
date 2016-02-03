from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/homecontroller/display/content/computer', permanent=False)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lightcontrol/', include("control_milight.urls")),
    url(r'^display/', include("display.urls")),
    url(r'^internet_connection/', include("info_internet_connection.urls")),
    url(r'^repeating_tasks/', include("repeating_tasks.urls")),
    url(r'^server_power/', include("server_power.urls")),
    url(r'^air_quality/', include("info_air_quality.urls")),
    url(r'^weather/', include("info_weather.urls")),
    url(r'^timer/', include("info_timers.urls")),
    url(r'^birthdays/', include("info_birthdays.urls")),
    url(r'^electricity/', include("info_electricity.urls")),
    url(r'^printer/', include("control_printer.urls")),
    url(r'^control_display/', include("control_display.urls")),
    url(r'^torrents/', include("info_torrents.urls")),
    url(r'^transportation/', include("info_transportation.urls")),
    url(r'^music/', include("control_music.urls")),
    url(r'^ext_pages/', include("info_ext_pages.urls")),
    url(r'^notifications/', include("info_notifications.urls")),
    url(r'^nodes/', include("node_data_receiver.urls")),
)
