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
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore, DjangoMemoryJobStore

# job models
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.models import DjangoJob
from django_apscheduler.admin import DjangoJobAdmin, DjangoJobExecutionAdmin

#class DjangoJobAdmin(admin.ModelAdmin):
#    list_display = ('name', 'next_run_time')
#    search_fields = ('name',)
#class DjangoJobExecutionAdmin(admin.ModelAdmin):
#    list_display = ('job', 'status', 'run_time', 'duration')
#    list_filter = ('status', )

#admin.site.register(DjangoJob, DjangoJobAdmin)
admin.site.register(DjangoJob, DjangoJobAdmin)
admin.site.register(DjangoJobExecution, DjangoJobExecutionAdmin)

from jobs.models import Job
from homeauto.admin import enable, disable

class JobAdmin(admin.ModelAdmin):
    list_display = ('command', 'id', 'interval', 'enabled')
    list_filter = ('enabled',)
    actions = [enable, disable]
admin.site.register(Job, JobAdmin)

