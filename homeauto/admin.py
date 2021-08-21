
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

# global actions for objects
def make_discoverable(modeladmin, request, queryset):
    queryset.update(enabled=True)
make_discoverable.short_description = "Discoverable by HomeAuto"

def remove_discoverable(modeladmin, request, queryset):
    queryset.update(enabled=False)
remove_discoverable.short_description = "Hide from HomeAuto"

# global actions for objects
def enable(modeladmin, request, queryset):
    queryset.update(enabled=True)
enable.short_description = "Enable Selected"

def disable(modeladmin, request, queryset):
    queryset.update(enabled=False)
disable.short_description = "Disable Selected"


# log entry (activity log)
from django.contrib.admin.models import LogEntry

class adminLogEntry(admin.ModelAdmin):
    list_display = ('object_repr', 'action_flag', 'user', 'content_type', 'object_id')
    list_filter = ('action_flag', 'user', 'content_type')
    search_fields = ('object_repr',)

admin.site.register(LogEntry, adminLogEntry)

# house models
import homeauto.models as house

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'username', 'enabled')
    list_filter = ('enabled',)
    actions = [enable, disable]
class HouseMotionDetectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_id')
    list_filter = ('enabled','source')
    search_fields = ('name','source')
    actions = [enable, disable]
class HouseLightAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
    actions = [enable, disable]
class HouseLockAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
    actions = [enable, disable]
class HouseSensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
    actions = [enable, disable]
class HouseScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'source', 'source_type', 'source_id')
    list_filter = ('source', 'source_type')
    search_fields = ('name','source', 'source_type')
    actions = [enable, disable]



from django import forms

class TriggerForm(forms.ModelForm):
    class Meta:
        model = house.Trigger
        fields = ('name', 'enabled', 'trigger', 'lock')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
#        self.fields['city'].queryset = City.objects.none()

"""
    trigger = models.CharField(max_length=60,choices=TRIGGER_TYPES, default=DEFAULT)
    motion_detector = models.OneToOneField(HouseMotionDetector, on_delete=models.CASCADE, blank=True, null=True)
    sensor = models.OneToOneField(HouseSensor, on_delete=models.CASCADE, blank=True, null=True)
    lock = models.OneToOneField(HouseLock, on_delete=models.CASCADE, blank=True, null=True)
    window_start = models.TimeField(default=timezone.now)
    window_end = models.TimeField(default=timezone.now)
    external_schedule =  models.ForeignKey(HouseSchedule, on_delete=models.CASCADE, blank=True, null=True)
    external_schedule_delay = models.IntegerField(default=-1, verbose_name='Delay behind external schedule (minutes)')
    people =  models.ManyToManyField(Person, blank=True)
    people_has_left = models.BooleanField(default=False)
    people_has_arrived = models.BooleanField(default=False)
    security_panel = models.ForeignKey(Panel, on_delete=models.CASCADE, blank=True, null=True)
    security_armed_to = models.BooleanField(default=False, verbose_name="When person sets state to")
    security_changed_to = models.BooleanField(default=False, verbose_name="When state changes to")
    security_armed_state =  models.CharField(max_length=60,choices=Common.ARM_STATES, default=Common.DISARMED, verbose_name="Armed State")
    hvac_unit = models.ManyToManyField(System, blank=True)
    hvac_profile = models.CharField(max_length=60,choices=Common.HVAC_PROFILES, default=Common.HOME)
    hvac_value = models.IntegerField(default=0)
    hvac_hold = models.BooleanField(default=False)
    hvac_heat_mode = models.CharField(max_length=60,choices=Common.HVAC_HEAT_MODES, default=Common.OFF)
    event = models.OneToOneField(CustomEvent, on_delete=models.CASCADE, blank=True, null=True)


"""



class TriggerAdmin(admin.ModelAdmin):
    search_fields = ('name','trigger')
    list_display = ('name', 'enabled', 'trigger', 'id')
    list_filter = ('enabled', 'trigger')
#    change_form_template = 'trigger_edit.html'
    actions = [enable, disable]
#    form = TriggerForm

class ActionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'enabled', 'action', 'last_action_time')
    list_filter = ('enabled', 'action')
    actions = [enable, disable]

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

