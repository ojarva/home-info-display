from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'homedisplay.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^lightcontrol/', include("control_milight.urls")),
    url(r'^display/', include("display.urls")),
    url(r'^internet_connection/', include("info_internet_connection.urls")),
    url(r'^repeating_tasks/', include("repeating_tasks.urls")),
    url(r'^server_power/', include("server_power.urls")),
    url(r'^indoor_quality/', include("indoor_quality.urls")),
    url(r'^weather/', include("info_weather.urls")),
    url(r'^timer/', include("info_timers.urls")),
    url(r'^action_timer/', include("info_timed_actions.urls")),
    url(r'^birthdays/', include("info_birthdays.urls")),
    url(r'^electricity/', include("info_electricity.urls")),
)
