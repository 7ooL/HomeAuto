
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import AdminSite

from django import forms

import homeauto.models.wemo as wemo
import homeauto.models.hue as hue
import homeauto.models.decora as decora
import homeauto.models.house as house
import homeauto.models.vivint as vivint
import homeauto.models.infinity as infinity

admin.site.site_title = 'Home Auto Web Interface'
admin.site.site_header = 'Home Auto'
admin.site.site_url = 'http://ha:8080.com/'
admin.site.index_title = 'House Administration'
admin.site.index_template = 'admin/ha_index.html'

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'enabled')
    pass
admin.site.register(house.Zone, ZoneAdmin)

class JobAdmin(admin.ModelAdmin):
    list_display = ('command','id', 'interval', 'enabled')
    pass
admin.site.register(house.Job, JobAdmin)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','username', 'enabled')
    pass
admin.site.register(house.Account, AccountAdmin)

class NuggetAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled')
    pass
admin.site.register(house.Nugget, NuggetAdmin)

class HouseMotionDetectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','enabled', 'source', 'source_id')
    pass
admin.site.register(house.HouseMotionDetector, HouseMotionDetectorAdmin)

class HouseLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','enabled', 'source', 'source_type','source_id')
    list_filter = ('source', 'source_type')
    pass
admin.site.register(house.HouseLight, HouseLightAdmin)

class HouseLockAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','enabled', 'source', 'source_type','source_id')
    list_filter = ('source', 'source_type')
    pass
admin.site.register(house.HouseLock, HouseLockAdmin)

class HouseSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','enabled', 'source', 'source_type','source_id')
    list_filter = ('source', 'source_type')
    pass
admin.site.register(house.HouseSensor, HouseSensorAdmin)




class TriggerForm(forms.Form):
    name = forms.CharField(required=False)

def view(request):
    form = TriggerForm(initial={'name': 'Peter'})
    return render(request, 'trigger_edit.html', form=form)

class TriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'trigger')
    change_form_template = 'trigger_edit.html'
    pass
admin.site.register(house.Trigger, TriggerAdmin)

class ActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'action', 'last_action_time')
    pass
admin.site.register(house.Action, ActionAdmin)


class InfinityAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'ip', 'port','mode')
    pass
admin.site.register(infinity.Infinity, InfinityAdmin)

class InfStatusAdmin(admin.ModelAdmin):
    list_display = ("infinity", "current_activity", "heat_mode", "filtrlvl", "hold", "fan", "vaca_running")
    pass
admin.site.register(infinity.InfStatus, InfStatusAdmin)

class InfProfileAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'name', 'fan', 'clsp', 'htsp')
    list_filter = ('infinity', 'name')
    pass
admin.site.register(infinity.InfProfile, InfProfileAdmin)

class InfActivityAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'activity', 'enabled', 'time', 'day', 'period')
    list_filter = ('infinity', 'activity', 'day', 'period', 'enabled')
    pass
admin.site.register(infinity.InfActivity, InfActivityAdmin)




class WemoAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'type', 'status', 'enabled')
    pass
admin.site.register(wemo.Wemo, WemoAdmin)

class DecoraSwitchAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'model', 'power', 'enabled')
    pass
admin.site.register(decora.Switch, DecoraSwitchAdmin)

class HueGroupAdmin(admin.ModelAdmin):
    list_display = ('name','id', 'type', 'on', 'enabled')
    pass
admin.site.register(hue.Group, HueGroupAdmin)

class HueLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','type', 'modelid', 'on', 'enabled')
    list_filter = ('type', 'modelid', 'on', 'enabled')
    pass
admin.site.register(hue.Light, HueLightAdmin)

class HueSceneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'enabled')
    pass
admin.site.register(hue.Scene, HueSceneAdmin)

class HueBridgeAdmin(admin.ModelAdmin):
    list_display = ('ip', 'id','alarm_use', 'count_down_lights', 'enabled')
    pass
admin.site.register(hue.Bridge, HueBridgeAdmin)

admin.site.register(hue.SceneLightstate)

class HueSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','presence', 'productname', 'lastupdated', 'battery', 'enabled')
    pass
admin.site.register(hue.Sensor, HueSensorAdmin)

class HueScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','localtime', 'enabled')
    pass
admin.site.register(hue.Schedule, HueScheduleAdmin)

class VivintPanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','armed_state', 'street', 'city')
    pass
admin.site.register(vivint.Panel, VivintPanelAdmin)

class VivintDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'state', 'type', 'enabled')
    list_filter = ('state', 'type', 'enabled')
    pass
admin.site.register(vivint.Device, VivintDeviceAdmin)


# Define an inline admin descriptor for Person model
# which acts a bit like a singleton
class PersonInline(admin.StackedInline):
    model = house.Person
    can_delete = False
    verbose_name_plural = 'Home Auto Options'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
