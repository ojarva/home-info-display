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
)
