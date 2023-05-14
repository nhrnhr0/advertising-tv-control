from django.contrib import admin

# Register your models here.
from .models import BetweenDateSchedule, BroadcastInTvs, BroadcastInTvsSchedule, ManualControlSchedule, PlaysCoutdownSchedule, Tv, Broadcast,BroadcastInTv,playedBroadcast,BusinessType

class BroadcastInline(admin.TabularInline):
    model = Tv.broadcasts.through
    extra = 1
    
class openingHoursInline(admin.TabularInline):
    from core.models import TvOpeningHours
    model = TvOpeningHours
    extra = 1

# Tv admin
class TvAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created', 'updated','pi_admin_link','pi__cec_hdmi_status', 'pi__humanize_socket_status_updated_ago','order')
    list_editable = ('order',)
    inlines = [BroadcastInline, openingHoursInline]
admin.site.register(Tv, TvAdmin)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('name','media_type', 'created', 'updated','publisher',)
    list_editable = ('publisher',)
admin.site.register(Broadcast, BroadcastAdmin)
class BroadcastInTvAdmin(admin.ModelAdmin):
    list_display = ('tv', 'broadcast', 'duration', 'created', 'updated',)
admin.site.register(BroadcastInTv, BroadcastInTvAdmin)

class BroadcastInTvsAdmin(admin.ModelAdmin):
    list_display = ('id','broadcast','duration','created','updated', 'tvs_list')
    def tvs_list(self, obj):
        return ", ".join([tv.name for tv in obj.tvs.all()])
admin.site.register(BroadcastInTvs, BroadcastInTvsAdmin)

class BroadcastInTvsScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', )
    pass
admin.site.register(BroadcastInTvsSchedule, BroadcastInTvsScheduleAdmin)
class PlaysCoutdownScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'plays_left','telegram_notification_in','telegram_notification_sent',)
    pass
admin.site.register(PlaysCoutdownSchedule, PlaysCoutdownScheduleAdmin)
class BetweenDateScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'end_date', )
    pass
admin.site.register(BetweenDateSchedule, BetweenDateScheduleAdmin)
class ManualControlScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active_bool',)
    pass
admin.site.register(ManualControlSchedule, ManualControlScheduleAdmin)

class playedBroadcastAdmin(admin.ModelAdmin):
    list_display = ('id','tv','broadcast','time','uri_key','is_approved')
    list_filter = ('is_approved','broadcast__publisher','broadcast', 'tv', 'time',)
    search_fields = ('tv__name','broadcast__name', 'broadcast__publisher__name', )
    
admin.site.register(playedBroadcast, playedBroadcastAdmin)


class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(BusinessType, BusinessTypeAdmin)