from django.contrib import admin

# Register your models here.
from .models import Tv, Broadcast,BroadcastInTv

class BroadcastInline(admin.TabularInline):
    model = Tv.broadcasts.through
    extra = 1

# Tv admin
class TvAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'updated',)
    inlines = [BroadcastInline]
admin.site.register(Tv, TvAdmin)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('name','media_type', 'created', 'updated',)
admin.site.register(Broadcast, BroadcastAdmin)
class BroadcastInTvAdmin(admin.ModelAdmin):
    list_display = ('tv', 'broadcast', 'duration', 'created', 'updated',)
admin.site.register(BroadcastInTv, BroadcastInTvAdmin)