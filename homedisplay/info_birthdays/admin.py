from django.contrib import admin
from .models import Birthday


class BirthdaysAdmin(admin.ModelAdmin):
    list_display = ("name", "nickname", "birthday")

admin.site.register(Birthday, BirthdaysAdmin)
