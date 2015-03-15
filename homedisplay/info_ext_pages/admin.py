from django.contrib import admin
from .models import ExtPage

class ExtPageAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "url")

admin.site.register(ExtPage, ExtPageAdmin)
