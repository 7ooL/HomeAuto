
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):

    def index(self, request, extra_context=None):
        all_users= User.objects.all()
        extra_context = extra_context or {"all_users":all_users }
#        print(extra_context)
        return super(MyAdminSite, self).index(request, extra_context)

from django.contrib import admin

admin.site = MyAdminSite()
admin.site.site_title = 'Home Auto Web Interface'
admin.site.site_header = 'Home Auto'
admin.site.site_url = 'http://ha:8080.com/'
admin.site.index_title = 'House Administration'
admin.site.index_template = 'admin/ha_index.html'

# job models
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.models import DjangoJob

class DjangoJobAdmin(admin.ModelAdmin):
    list_display = ('name', 'next_run_time')
    search_fields = ('name',)
class DjangoJobExecutionAdmin(admin.ModelAdmin):
    list_display = ('job', 'status', 'run_time', 'duration')
    list_filter = ('status', )

admin.site.register(DjangoJob, DjangoJobAdmin)
admin.site.register(DjangoJobExecution, DjangoJobExecutionAdmin)

# house models
import homeauto.models.house as house

class JobAdmin(admin.ModelAdmin):
    list_display = ('command', 'id', 'interval', 'enabled')
    list_filter = ('enabled',)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'username', 'enabled')
    list_filter = ('enabled',)
class HouseMotionDetectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_id')
    list_filter = ('enabled','source')
    search_fields = ('name','source')
class HouseLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
class HouseLockAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
class HouseSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
class HouseScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
class TriggerAdmin(admin.ModelAdmin):
    search_fields = ('name','trigger')
    list_display = ('name', 'enabled', 'trigger', 'id')
    list_filter = ('enabled', 'trigger')
    change_form_template = 'trigger_edit.html'
class ActionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'enabled', 'action', 'last_action_time')
    list_filter = ('enabled', 'action')

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
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

admin.site.register(house.Action, ActionAdmin)
admin.site.register(house.HouseMotionDetector, HouseMotionDetectorAdmin)
admin.site.register(house.HouseLight, HouseLightAdmin)
admin.site.register(house.HouseLock, HouseLockAdmin)
admin.site.register(house.HouseSensor, HouseSensorAdmin)
admin.site.register(house.HouseSchedule, HouseScheduleAdmin)
admin.site.register(house.Trigger, TriggerAdmin)
admin.site.register(house.Account, AccountAdmin)
admin.site.register(house.CustomEvent)
admin.site.register(house.Job, JobAdmin)
admin.site.register(house.Nugget, NuggetAdmin)

# user models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class PersonInline(admin.StackedInline):
    model = house.Person
    can_delete = False
    verbose_name_plural = 'Home Auto Options'

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_home')
    def is_home(self, obj):
        return house.Person.objects.get(user=obj.id).is_home
    inlines = (PersonInline,)

admin.site.register(User, UserAdmin)

# carrier infinity models
import homeauto.models.infinity as infinity

class InfinityAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'ip', 'port', 'mode')
class InfStatusAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'current_activity', 'heat_mode', 'filtrlvl', 'hold', 'fan', 'vaca_running')
class InfProfileAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'name', 'fan', 'clsp', 'htsp')
    list_filter = ('infinity', 'name')
class InfActivityAdmin(admin.ModelAdmin):
    list_display = ('infinity', 'activity', 'enabled', 'time', 'day', 'period')
    list_filter = ('infinity', 'activity', 'day', 'period', 'enabled')

admin.site.register(infinity.InfStatus, InfStatusAdmin)
admin.site.register(infinity.InfProfile, InfProfileAdmin)
admin.site.register(infinity.Infinity, InfinityAdmin)
admin.site.register(infinity.InfActivity, InfActivityAdmin)

# watcher model
import homeauto.models.watcher as watcher

class WatcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'directory')
    search_fields = ('name',)

admin.site.register(watcher.Directory, WatcherAdmin)

# wemo models
import homeauto.models.wemo as wemo

class WemoAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'status', 'enabled')
    list_filter = ('type','status','enabled')
    search_fields = ('name',)

admin.site.register(wemo.Wemo, WemoAdmin)

# decora models
import homeauto.models.decora as decora

class DecoraSwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'model', 'power', 'enabled')
    list_filter = ('model','power','enabled')
    search_fields = ('name',)

admin.site.register(decora.Switch, DecoraSwitchAdmin)

# vivint models
import homeauto.models.vivint as vivint

class VivintPanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'armed_state', 'street', 'city')
class VivintDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'state', 'type', 'enabled')
    list_filter = ('state', 'type', 'enabled')
    search_fields = ('name','state','type')

admin.site.register(vivint.Panel, VivintPanelAdmin)
admin.site.register(vivint.Device, VivintDeviceAdmin)

# hue models
import homeauto.models.hue as hue

class HueGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'on', 'enabled')
    list_filter = ('type','on','enabled')
    search_fields = ('name',)
class HueLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'type', 'modelid', 'on', 'enabled')
    list_filter = ('type', 'modelid', 'on', 'enabled')
    search_fields = ('name',)
class HueSceneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group', 'enabled')
    list_filter = ('group','enabled')
    search_fields = ('name',)
class HueBridgeAdmin(admin.ModelAdmin):
    list_display = ('ip', 'id', 'alarm_use', 'count_down_lights', 'enabled')
class HueSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'presence', 'productname', 'lastupdated', 'battery','enabled')
    list_filter = ('presence','enabled', 'productname')
    search_fields = ('name','productname')
class HueScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'localtime', 'enabled')
    search_fields = ('name',)

admin.site.register(hue.Schedule, HueScheduleAdmin)
admin.site.register(hue.SceneLightstate)
admin.site.register(hue.Sensor, HueSensorAdmin)
admin.site.register(hue.Bridge, HueBridgeAdmin)
admin.site.register(hue.Scene, HueSceneAdmin)
admin.site.register(hue.Light, HueLightAdmin)
admin.site.register(hue.Group, HueGroupAdmin)






