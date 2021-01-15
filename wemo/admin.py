from django.contrib import admin
import wemo.models as wemo
from homeauto.admin import make_discoverable, remove_discoverable


class WemoAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'status', 'enabled')
    list_filter = ('type','status','enabled')
    search_fields = ('name',)
    actions = [make_discoverable, remove_discoverable]

admin.site.register(wemo.Device, WemoAdmin)

