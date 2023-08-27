from django.contrib import admin
from  core.models import Publisher,PublisherType, OpeningHours
# class UserBroadcastsInline(admin.TabularInline):
#     model = Publisher.broadcasts.through
#     extra = 1
    
# Register your models here.
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    # inlines = [UserBroadcastsInline,]
    # filter_horizontal = ('broadcasts',)
    list_filter = ('name',)
    search_fields = ('name',)
    filter_horizontal=('publishers_types',)
admin.site.register(Publisher, PublisherAdmin)

class PublisherTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('name',)
admin.site.register(PublisherType, PublisherTypeAdmin)

class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('id', 'weekday','from_hour','to_hour',)
    list_filter = ('weekday','from_hour','to_hour',)
admin.site.register(OpeningHours, OpeningHoursAdmin)