from django.contrib import admin
from .models import LightAutomation, LightGroup

class LightGroupAdmin(admin.ModelAdmin):
    list_display = ("group_id", "description", "on")
    fields = ("description",)
    readonly_fields = ("group_id", "on", "color", "rgbw_brightness", "white_brightness")

admin.site.register(LightGroup, LightGroupAdmin)

class LightAutomationAdmin(admin.ModelAdmin):
    list_display = ("action", "running", "start_time", "duration", "active_days", "action_if_off", "set_white", "no_brighten", "no_dimming")

admin.site.register(LightAutomation, LightAutomationAdmin)
