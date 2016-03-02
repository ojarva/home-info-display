from django.contrib import admin
from .models import CustomLabel, TimedCustomLabel


class CustomLabelAdmin(admin.ModelAdmin):
    list_display = ("name",)

admin.site.register(CustomLabel, CustomLabelAdmin)


class TimedCustomLabelAdmin(admin.ModelAdmin):
    list_display = ("name", "duration")

admin.site.register(TimedCustomLabel, TimedCustomLabelAdmin)
