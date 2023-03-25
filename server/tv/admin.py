from django.contrib import admin

# Register your models here.
from .models import Tv, Broadcast,BroadcastInTv,playedBroadcast,BusinessType

class BroadcastInline(admin.TabularInline):
    model = Tv.broadcasts.through
    extra = 1
    
class openingHoursInline(admin.TabularInline):
    from core.models import TvOpeningHours
    model = TvOpeningHours
    extra = 1

# Tv admin
class TvAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created', 'updated','pi_admin_link','pi__cec_hdmi_status', 'pi__humanize_socket_status_updated_ago',)
    inlines = [BroadcastInline, openingHoursInline]
admin.site.register(Tv, TvAdmin)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('name','media_type', 'created', 'updated','publisher',)
    list_editable = ('publisher',)
admin.site.register(Broadcast, BroadcastAdmin)
class BroadcastInTvAdmin(admin.ModelAdmin):
    list_display = ('tv', 'broadcast', 'duration', 'created', 'updated',)
admin.site.register(BroadcastInTv, BroadcastInTvAdmin)


class playedBroadcastAdmin(admin.ModelAdmin):
    list_display = ('id','uuid','tv','broadcast','time','uri_key','is_approved')
admin.site.register(playedBroadcast, playedBroadcastAdmin)


class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(BusinessType, BusinessTypeAdmin)