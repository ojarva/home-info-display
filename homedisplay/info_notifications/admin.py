from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("item_type", "description", "level",)

admin.site.register(Notification, NotificationAdmin)
