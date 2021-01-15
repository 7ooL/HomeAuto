from django.contrib import admin
import carrier.models as Carrier
from homeauto.admin import make_discoverable, remove_discoverable

class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'ip', 'port', 'mode')
class StatusAdmin(admin.ModelAdmin):
    list_display = ('system', 'current_activity', 'heat_mode', 'filtrlvl', 'hold', 'fan', 'vaca_running')
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('system', 'name', 'fan', 'clsp', 'htsp')
    list_filter = ('system', 'name')
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('system', 'activity', 'enabled', 'time', 'day', 'period')
    list_filter = ('system', 'activity', 'day', 'period', 'enabled')

admin.site.register(Carrier.Status, StatusAdmin)
admin.site.register(Carrier.Profile, ProfileAdmin)
admin.site.register(Carrier.System, SystemAdmin)
admin.site.register(Carrier.Activity, ActivityAdmin)


