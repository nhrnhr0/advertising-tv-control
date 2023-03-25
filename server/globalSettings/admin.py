from django.contrib import admin
from .models import GlobalSettings
# Register your models here.
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('id','turn_off_all_tvs',)
    filter_horizontal = ('defult_broadcasts',)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)