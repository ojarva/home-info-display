from django.contrib import admin
from .models import Birthday

class BirthdaysAdmin(admin.ModelAdmin):
    pass

admin.site.register(Birthday, BirthdaysAdmin)
