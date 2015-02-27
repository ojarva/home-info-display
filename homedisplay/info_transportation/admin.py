from django.contrib import admin
from .models import Stop, Line, LineShow

class LineShowAdmin(admin.ModelAdmin):
    list_display = ("description", "show_days", "show_start", "show_end")

admin.site.register(LineShow, LineShowAdmin)



class LineAdminInline(admin.TabularInline):
    model = Line
    extra = 0
    fieldsets = (
        (
            None,
            {
                'fields': ('line_number', 'show_line', 'icon', 'show_times'),
            }
        ),
    )
    readonly_fields = ('line_number_raw',)


class StopAdmin(admin.ModelAdmin):
    list_display = ("description", "stop_number")
    inlines = (LineAdminInline,)

admin.site.register(Stop, StopAdmin)
