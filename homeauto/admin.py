from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import AdminSite
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

import homeauto.models.watcher as watcher
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

class CustomAdminSite(admin.AdminSite):

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        all_users= User.objects.all()
        extra_context['all_users'] = {'all_users': all_users}
        # Add your context here
        return super(CustomAdminSite, self).index(request, extra_context)

site = CustomAdminSite

admin.site.register(hue.SceneLightstate)
admin.site.register(house.CustomEvent)

class JobAdmin(admin.ModelAdmin):
    list_display = ('command', 'id', 'interval', 'enabled')
admin.site.register(house.Job, JobAdmin)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'username', 'enabled')
admin.site.register(house.Account, AccountAdmin)

class NuggetAdmin(admin.ModelAdmin):

    def trigger_name(self, obj):
        display_text = "<br> ".join([
            "<a href={}>{}</a>".format(reverse('admin:{}_{}_change'.format(trigger._meta.app_label, trigger._meta.model_name),args=(trigger.pk,)),trigger.name)
             if trigger.enabled
             else "<a class='redStrike' href={}>{}</a>".format(reverse('admin:{}_{}_change'.format(trigger._meta.app_label, trigger._meta.model_name),args=(trigger.pk,)),trigger.name)
             for trigger in obj.triggers.all()
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"

    def action_name(self, obj):
        display_text = "<br> ".join([
            "<a href={}>{}</a>".format(reverse('admin:{}_{}_change'.format(action._meta.app_label, action._meta.model_name),args=(action.pk,)),action.name)
             if action.enabled
             else "<a class='redStrike' href={}>{}</a>".format(reverse('admin:{}_{}_change'.format(action._meta.app_label, action._meta.model_name),args=(action.pk,)),action.name)
             for action in obj.actions.all()
        ])
        if display_text:
            return mark_safe(display_text)
        return "-"

#    def trigger_count(self, obj):
#        return obj.triggers.count()
#    trigger_count.short_description = "Trigger Count"

#    def action_count(self, obj):
#        return obj.actions.count()
#    action_count.short_description = "Action Count"

    search_fields = ( 'name','triggers__name', 'actions__name')
    list_filter = ('enabled', 'only_execute_if_someone_is_home')
    list_display = ('name', 'enabled', 'only_execute_if_someone_is_home', 'trigger_name', 'action_name', 'id')

admin.site.register(house.Nugget, NuggetAdmin)

class HouseMotionDetectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_id')
admin.site.register(house.HouseMotionDetector, HouseMotionDetectorAdmin)

class HouseLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
admin.site.register(house.HouseLight, HouseLightAdmin)

class HouseLockAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
admin.site.register(house.HouseLock, HouseLockAdmin)

class HouseSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
admin.site.register(house.HouseSensor, HouseSensorAdmin)

class HouseScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
admin.site.register(house.HouseSchedule, HouseScheduleAdmin)

class TriggerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'enabled', 'trigger', 'id')
    list_filter = ('enabled', 'trigger')
    change_form_template = 'trigger_edit.html'
admin.site.register(house.Trigger, TriggerAdmin)

class ActionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'enabled', 'action', 'last_action_time')
    list_filter = ('enabled', 'action')
admin.site.register(house.Action, ActionAdmin)

class InfinityAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'ip', 'port', 'mode')
admin.site.register(infinity.Infinity, InfinityAdmin)

class InfStatusAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'current_activity', 'heat_mode', 'filtrlvl', 'hold', 'fan', 'vaca_running')
admin.site.register(infinity.InfStatus, InfStatusAdmin)

class InfProfileAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'name', 'fan', 'clsp', 'htsp')
    list_filter = ('infinity', 'name')
admin.site.register(infinity.InfProfile, InfProfileAdmin)

class InfActivityAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'activity', 'enabled', 'time', 'day', 'period')
    list_filter = ('infinity', 'activity', 'day', 'period', 'enabled')
admin.site.register(infinity.InfActivity, InfActivityAdmin)

class WemoAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'status', 'enabled')
admin.site.register(wemo.Wemo, WemoAdmin)

class WatcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'directory')
admin.site.register(watcher.Directory, WatcherAdmin)

class DecoraSwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'model', 'power', 'enabled')
admin.site.register(decora.Switch, DecoraSwitchAdmin)

class HueGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'on', 'enabled')
admin.site.register(hue.Group, HueGroupAdmin)

class HueLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'modelid', 'on', 'enabled')
    list_filter = ('type', 'modelid', 'on', 'enabled')
admin.site.register(hue.Light, HueLightAdmin)

class HueSceneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'enabled')
admin.site.register(hue.Scene, HueSceneAdmin)

class HueBridgeAdmin(admin.ModelAdmin):
    list_display = ('ip', 'id', 'alarm_use', 'count_down_lights', 'enabled')
admin.site.register(hue.Bridge, HueBridgeAdmin)

class HueSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'presence', 'productname', 'lastupdated', 'battery','enabled')
admin.site.register(hue.Sensor, HueSensorAdmin)

class HueScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'localtime', 'enabled')
admin.site.register(hue.Schedule, HueScheduleAdmin)

class VivintPanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'armed_state', 'street', 'city')
admin.site.register(vivint.Panel, VivintPanelAdmin)

class VivintDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'state', 'type', 'enabled')
    list_filter = ('state', 'type', 'enabled')
admin.site.register(vivint.Device, VivintDeviceAdmin)

class PersonInline(admin.StackedInline):
    model = house.Person
    can_delete = False
    verbose_name_plural = 'Home Auto Options'

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_home')
    def is_home(self, obj):
        return house.Person.objects.get(user=obj.id).is_home
    inlines = (PersonInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
