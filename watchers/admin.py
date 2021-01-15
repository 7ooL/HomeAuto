from django.contrib import admin
import watchers.models as watcher
from homeauto.admin import make_discoverable, remove_discoverable

# watcher model

class WatcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'enabled', 'directory')
    search_fields = ('name',)
    actions = [make_discoverable, remove_discoverable]

admin.site.register(watcher.Directory, WatcherAdmin)

