from django.contrib import admin
from .models import PrintLabel

class PrintLabelAdmin(admin.ModelAdmin):
    list_display = ("name", "content", "include_date", "include_time")

admin.site.register(PrintLabel, PrintLabelAdmin)
