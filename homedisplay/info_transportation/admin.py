from django.contrib import admin
from .models import Stop, Line

class LineAdminInline(admin.TabularInline):
    model = Line
    extra = 0
    fieldsets = (
        (
            None,
            {
                'fields': ('line_number',)
            }
        ),
    )

class StopAdmin(admin.ModelAdmin):
    list_display = ("description", "stop_number")
    inlines = (LineAdminInline,)

admin.site.register(Stop, StopAdmin)
