from django.contrib import admin
from .models import Stop, Line

class LineAdminInline(admin.TabularInline):
    model = Line
    extra = 0
    fieldsets = (
        (
            None,
            {
                'fields': ('line_number', 'show_line', 'icon'),
            }
        ),
    )
    readonly_fields = ('line_number_raw',)


class StopAdmin(admin.ModelAdmin):
    list_display = ("description", "stop_number")
    inlines = (LineAdminInline,)

admin.site.register(Stop, StopAdmin)
