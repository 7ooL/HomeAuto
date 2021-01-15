from django.contrib import admin
import hue.models as hue
from homeauto.admin import make_discoverable, remove_discoverable

class HueGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'on', 'enabled')
    list_filter = ('type','on','enabled')
    search_fields = ('name',)
    actions = [make_discoverable, remove_discoverable]
class HueLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'modelid', 'on', 'enabled')
    list_filter = ('type', 'modelid', 'on', 'enabled')
    actions = [make_discoverable, remove_discoverable]
    search_fields = ('name',)
class HueSceneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'enabled', 'owner')
    list_filter = ('group','enabled', 'owner')
    search_fields = ('name','id','owner')
    actions = [make_discoverable, remove_discoverable]
class HueBridgeAdmin(admin.ModelAdmin):
    list_display = ('ip', 'id', 'alarm_use', 'count_down_lights', 'enabled')
    actions = [make_discoverable, remove_discoverable]
class HueSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'presence', 'productname', 'lastupdated', 'battery','enabled')
    list_filter = ('presence','enabled', 'productname')
    actions = [make_discoverable, remove_discoverable]
    search_fields = ('name','productname')
class HueScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'localtime', 'enabled')
    search_fields = ('name',)
    actions = [make_discoverable, remove_discoverable]

admin.site.register(hue.Schedule, HueScheduleAdmin)
admin.site.register(hue.SceneLightstate)
admin.site.register(hue.Sensor, HueSensorAdmin)
admin.site.register(hue.Bridge, HueBridgeAdmin)
admin.site.register(hue.Scene, HueSceneAdmin)
admin.site.register(hue.Light, HueLightAdmin)
admin.site.register(hue.Group, HueGroupAdmin)
