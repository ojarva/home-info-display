from django.contrib import admin
from .models import Stop, Line

class PersonToRollingPersonInline(admin.TabularInline):
    model = RollingPerson
    extra = 0
    fieldsets = (
        (
            None,
            {
                'fields': ('project', 'start_date', 'end_date', 'windows', 'ios', 'android', 'front', 'back', 'ux', 'qa', 'pm', 'consulting', 'na', 'seniority')
            }
        ),
    )

class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "tribe", "ext", "skills", "days_per_week", "utz_target")
    inlines = (PersonToRollingPersonInline,)

class StopAdmin(admin.ModelAdmin):
    list_display = ("description", "stop_number")
    inlines = (,)

admin.site.register(Stop, StopAdmin)
