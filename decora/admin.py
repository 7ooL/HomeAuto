from django.contrib import admin
import decora.models as decora
from homeauto.admin import make_discoverable, remove_discoverable

class SwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'model', 'power', 'enabled')
    list_filter = ('model','power','enabled')
    search_fields = ('name',)
    actions = [make_discoverable, remove_discoverable]
class DecoraAccountAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(decora.Switch, SwitchAdmin)
admin.site.register(decora.Account, DecoraAccountAdmin)
