from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe
# Register your models here.
from .models import BetweenDateSchedule, BroadcastInTvs, BroadcastInTvsSchedule, ManualControlSchedule, PlaysCoutdownSchedule, Tv, Broadcast,BroadcastInTv,playedBroadcast,BusinessType, DefaultTvFotter,TvFotter

# class BroadcastInline(admin.TabularInline):
#     model = Tv.broadcasts.through
#     extra = 1


class DefaultTvFotterAdmin(admin.ModelAdmin):
    list_display = ('location_name','index_in_tv','image_display', 'updated','created',)
    
    def image_display(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.image.url,
            width="50px",
            height="50px",
            ))
        pass

    def image_display(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.image.url,
            width="50px",
            height="50px",
            ))
        pass
    
    
    pass
admin.site.register(DefaultTvFotter, DefaultTvFotterAdmin)


from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.db.models import Q

class TvFotterIsActiveFilter(SimpleListFilter):
    title = 'active' # or use _('country') for translated title
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('active', 'active'),
            ('inactive', 'inactive'),
        )
        
    def queryset(self, request, queryset):
        if self.value() == 'active':
            # call is_active_prop from models.py
            return queryset.filter(Q(end_date__isnull=True) | Q(end_date__gte=timezone.now()))
            
        if self.value() == 'inactive':
            # call is_active_prop from models.py
            return queryset.filter(end_date__lt=timezone.now())
        return queryset

class TvFotterAdmin(admin.ModelAdmin):
    list_display = ('title_trim','is_active', 'image_display','end_date','location_default_display','tv_link','updated','created',)
    list_filter = ('location_default','tv',TvFotterIsActiveFilter)
    search_fields = ('title','tv__name','location_default__location_name',)
    def title_trim(self, obj):
        return obj.title[:15]
    def tv_link(self, obj):
        if obj.tv is None:
            return ""
        return mark_safe('<a href="/admin/tv/tv/%s/change/">%s</a>' % (obj.tv.id, obj.tv.name))
    def image_display(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.image.url,
            width="50px",
            height="50px",
            ))
        pass
    pass

    def location_default_display(self, obj):
        ret = ""
        if obj.location_default:
            ret = obj.location_default.location_name + "<br>"
            ret += '<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.location_default.image.url,
            width="50px",
            height="50px",
            )
        return mark_safe(ret)
admin.site.register(TvFotter, TvFotterAdmin)

class openingHoursInline(admin.TabularInline):
    from core.models import TvOpeningHours
    model = TvOpeningHours
    extra = 1

# Tv admin
class TvAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'created', 'updated','pi_admin_link','pi__humanize_socket_status_updated_ago','spots_status','get_tv_fotters_count')
    list_editable = ()
    autocomplete_fields = ('pi',)
    search_fields = ('name','address','phone','email','contact_name','contact_phone','pi__name',)
    
    fields =('name','address','manual_turn_off','phone','email','contact_name','contact_phone','pi','updated','created','uri_key','order','spots_status','get_spots_display','get_filler_display',  'fotter_display',)
    readonly_fields = ('updated','created','fotter_display','get_tv_fotters_count','spots_status','get_spots_display','get_filler_display',)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        # ('spots','spots__priceing_plan','spots__assets',)
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('spots','spots__priceing_plan','spots__assets','pi')
        return qs
        
    
    def spots_status(self, obj):
        ret = "<div>"
        data = obj.calculate_spots_status()
        prc = "{:.2f}".format(data['loop_full_prc'])
        # אחוז מלא מהלופ
        ret += f"מפרסמים פעילים: {len(data['spots'])}<br>"
        ret += f"פילרים: {len(data['fillers'])}<br>"
        ret += f"<progress value=\"{prc}\" max=\"100\"></progress><br>"
        ret += f"{prc}% מהלופ מלא <br>"
        ret += f"</div>"
        return mark_safe(ret)
        pass
    
    def fotter_display(self, obj):
        ret = "<div style='width: 100%;overflow-x: auto;display: flex;flex-direction:row;'>"
        fotters = obj.get_tv_fotters()
        for fotter in fotters:
            if fotter:
                ret += '<div class="wraper">'
                ret += "<img src='{}' style='width: 100px; height: 45px;'><br>".format(fotter.image.url)
                ret += "<b>{}</b><br>".format(fotter.title)
                ret += "</div>"
        ret += "</div>"
        # edit link: admin/tv/tvfotter/?tv__id__exact=<tv_id>
        if obj.id:
            ret += "<a href='/admin/tv/tvfotter/?tv__id__exact={}'>ערוך באנרים בתחתית המסך</a>".format(obj.id)
        return mark_safe(ret)

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
    list_display = ('id', 'name','price','description','plays_per_day','play_duration','secounds_per_day','updated','created',)
    search_fields = ('name','description','price', 'plays_per_day', 'play_duration',)

    pass
admin.site.register(PriceingPlen, PriceingPlenAdmin)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','media_display','media_type','updated','created',)
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
    list_display = ('id','name', 'is_active','priceing_plan', 'tvs_display','is_filler_admin_display','publisher','html_assets_display','start_at','end_at',)
    list_filter = ('publisher','priceing_plan','is_filler','tvs',)
    filter_horizontal = ('tvs',)
    fields = ('name','is_active','is_active_toggel','start_at','end_at','priceing_plan', 'publisher','is_filler','filler_duration','tvs','html_assets_display',)
    readonly_fields = ('html_assets_display','is_active', 'tvs_display','is_active')
    inlines = [NewAssetsInline,]
    autocomplete_fields = ('priceing_plan','publisher',)
    search_fields = ('publisher__name','priceing_plan__name','tvs__name', 'assets__name',)
    actions = ['make_active', 'make_inactive', 'make_filler', 'make_not_filler']
    
    def make_active(self, request, queryset):
        queryset.update(is_active_toggel=True)
    make_active.short_description = "הפוך לפעיל"

    def make_inactive(self, request, queryset):
        queryset.update(is_active_toggel=False)
    make_inactive.short_description = "הפוך ללא פעיל"
    
    def make_filler(self, request, queryset):
        queryset.update(is_filler=True)
    make_filler.short_description = "הפוך לפילר"
    
    def make_not_filler(self, request, queryset):
        queryset.update(is_filler=False)
    make_not_filler.short_description = "הפוך ללא פילר"
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related('assets','tvs').select_related('priceing_plan','publisher')
    
    def is_filler_admin_display(self, obj):
        return 'FILLER (' + str(obj.get_duration()) + ')' if obj.is_filler else ''
    is_filler_admin_display.short_description = 'is_filler'
    
    
    
    

    # def is_active(self, obj):
    #     return obj.is_active
admin.site.register(Spot, SpotAdmin)