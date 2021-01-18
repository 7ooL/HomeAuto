from django.contrib import admin
import vivint.models as vivint
from homeauto.admin import make_discoverable, remove_discoverable

# vivint models
class VivintPanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'armed_state', 'street', 'city')
class VivintDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'state', 'type', 'enabled')
    list_filter = ('state', 'type', 'enabled')
    search_fields = ('name','state','type')
    actions = [make_discoverable, remove_discoverable]
class VivintAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'pubnub')


admin.site.register(vivint.Panel, VivintPanelAdmin)
admin.site.register(vivint.Device, VivintDeviceAdmin)
admin.site.register(vivint.Account, VivintAccountAdmin)


