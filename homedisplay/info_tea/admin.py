from django.contrib import admin
from .models import NfcTag


class NfcTagAdmin(admin.ModelAdmin):
    list_display = ("name", "boil_water")

admin.site.register(NfcTag, NfcTagAdmin)
