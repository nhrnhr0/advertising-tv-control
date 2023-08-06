from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe
# Register your models here.
from .models import BetweenDateSchedule, BroadcastInTvs, BroadcastInTvsSchedule, ManualControlSchedule, PlaysCoutdownSchedule, Tv, Broadcast,BroadcastInTv,playedBroadcast,BusinessType

# class BroadcastInline(admin.TabularInline):
#     model = Tv.broadcasts.through
#     extra = 1




class openingHoursInline(admin.TabularInline):
    from core.models import TvOpeningHours
    model = TvOpeningHours
    extra = 1

# Tv admin
class TvAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created', 'updated','pi_admin_link','pi__cec_hdmi_status', 'pi__humanize_socket_status_updated_ago','order',)
    list_editable = ('order',)
    autocomplete_fields = ('pi',)
    search_fields = ('name','address','phone','email','contact_name','contact_phone','pi__name',)
    
    fields =('name','address','manual_turn_off','phone','email','contact_name','contact_phone','pi','updated','created','uri_key','order',)
    readonly_fields = ('updated','created',)
    # def active_spots_html_display(self, obj):
    #     data = obj.get_active_spots()
    #     ret = ""
    #     for spot in data:
    #         ret += f"{spot.id}<br>"
    #     return mark_safe(ret)

    # def filler_spots_html_display(self, obj):
    #     data = obj.get_filler_spots()
    #     ret = ""
    #     for spot in data:
    #         ret += f"{spot.id}<br>"
    #     return mark_safe(ret)
    inlines = [openingHoursInline]
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



from .models import PriceingPlen, Asset, Spot
class PriceingPlenAdmin(admin.ModelAdmin):
    list_display = ('name','price','description','plays_per_day','play_duration',)
    search_fields = ('name','description','price', 'plays_per_day', 'play_duration',)

    pass
admin.site.register(PriceingPlen, PriceingPlenAdmin)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name','media_display','media_type','updated','created',)
    search_fields = ('name','media_type',)
    def media_display(self, obj):
        if obj.media_type == "video":
            return mark_safe('<video width="177.777778px" height="100px" controls><source src="{url}" type="video/mp4"></video>'.format(
            url = obj.media.url,
            ))
        return mark_safe('<img src="{url}" width="177.777778px" height="100px" />'.format(
            url = obj.media.url,
            ))
    pass
admin.site.register(Asset, AssetAdmin)


class NewAssetsInline(admin.TabularInline):
    model = Spot.assets.through
    extra = 3
class SpotAdmin(admin.ModelAdmin):
    list_display = ('id','is_active','start_at','end_at','priceing_plan', 'tvs_display','is_filler_admin_display','publisher','html_assets_display')
    list_filter = ('publisher','priceing_plan','is_filler','tvs',)
    filter_horizontal = ('tvs',)
    fields = ('is_active','is_active_toggel','start_at','end_at','priceing_plan', 'publisher','is_filler','filler_duration','tvs','html_assets_display',)
    readonly_fields = ('html_assets_display','is_active', 'tvs_display','is_active')
    inlines = [NewAssetsInline,]
    autocomplete_fields = ('priceing_plan','publisher',)
    search_fields = ('publisher__name','priceing_plan__name','tvs__name', 'assets__name',)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('assets','tvs').select_related('priceing_plan','publisher')
    
    def is_filler_admin_display(self, obj):
        return 'FILLER (' + str(obj.get_duration()) + ')' if obj.is_filler else ''
    
    
    
    
    

    # def is_active(self, obj):
    #     return obj.is_active
admin.site.register(Spot, SpotAdmin)