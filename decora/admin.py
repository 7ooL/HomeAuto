from django.contrib import admin
from .models import Switch
from homeauto.admin import make_discoverable, remove_discoverable

class SwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'model', 'power', 'enabled')
    list_filter = ('model','power','enabled')
    search_fields = ('name',)
    actions = [make_discoverable, remove_discoverable]

admin.site.register(Switch, SwitchAdmin)
