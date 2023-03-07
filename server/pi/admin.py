from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PiDevice
from django.contrib import messages
import json
# messages.add_message(request, messages.INFO, 'Hello world.')

# Register your models here.
class PiDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_approved','image_tag', 'name','cec_hdmi_status','humanize_socket_status_updated_ago','device_id', 'tv_admin_link',)
    list_filter = ('device_id','name','cec_hdmi_status','socket_status_updated',)
    actions = ['approve','reboot_device', 'hdmi_cec_off','hdmi_cec_on','relaunch_kiosk_browser','set_tv_url']
    
    
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
        messages.add_message(request, messages.INFO, 'Approved')
    approve.short_description = "Approve selected devices"
    
    def reboot_device(self, request, queryset):
        results = []
        for obj in queryset:
            result = obj.send_reboot_device()
            results.append(result.text)
        messages.add_message(request, messages.INFO, json.dumps(results))
    def hdmi_cec_off(self, request, queryset):
        results = []
        for obj in queryset:
            result = obj.send_cec_off()
            results.append(result.text)
        messages.add_message(request, messages.INFO, json.dumps(results))
    
    def hdmi_cec_on(self, request, queryset):
        results = []
        for obj in queryset:
            result = obj.send_cec_on()
            results.append(result.text)
        messages.add_message(request, messages.INFO, json.dumps(results))    
        
    def relaunch_kiosk_browser(self, request, queryset):
        results = []
        for obj in queryset:
            result = obj.send_relaunch_kiosk_browser()
            results.append(result.text)
        messages.add_message(request, messages.INFO, json.dumps(results))
    
    def set_tv_url(self, request, queryset):
        results = []
        for obj in queryset:
            result = obj.send_set_tv_url()
            results.append(result.text)
        messages.add_message(request, messages.INFO, json.dumps(results))
admin.site.register(PiDevice, PiDeviceAdmin)
