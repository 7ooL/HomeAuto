import time
from datetime import timedelta

from apscheduler import events
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Avg
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from django_apscheduler.models import DjangoJob, DjangoJobExecution
from django_apscheduler.admin import DjangoJobAdmin, DjangoJobExecutionAdmin
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore, DjangoMemoryJobStore

from django import forms
from .fields import GroupedModelChoiceField
from .models import Command, Group, Job

admin.site.register(DjangoJob, DjangoJobAdmin)
admin.site.register(DjangoJobExecution, DjangoJobExecutionAdmin)

class CommandAdmin(admin.ModelAdmin):
    list_display = ('name','group')
admin.site.register(Command, CommandAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Group, GroupAdmin)


def enable(modeladmin, request, queryset):
    for obj in queryset:
        obj.enabled=True
        obj.save()
enable.short_description = "Enable Selected"

def disable(modeladmin, request, queryset):
    for obj in  queryset:
        obj.enabled=False
        obj.save()
disable.short_description = "Disable Selected"

class JobForm(forms.ModelForm):
    command = GroupedModelChoiceField(
        queryset=Command.objects.exclude(group=None),
        choices_groupby='group'
    )

    class Meta:
        model = Job
        fields = ('command', 'interval', 'enabled')

class JobAdmin(admin.ModelAdmin):
    list_display = ('command', 'id', 'interval', 'enabled')
    list_filter = ('enabled',)
    actions = [enable, disable]
    form = JobForm

admin.site.register(Job, JobAdmin)

