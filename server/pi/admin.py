from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PiDevice
from django.contrib import messages
import json
# messages.add_message(request, messages.INFO, 'Hello world.')

# Register your models here.
class PiDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'name','cec_hdmi_status','is_socket_connected_live','humanize_socket_status_updated_ago','device_id', 'tv_admin_link',)
    list_filter = ('device_id','name','cec_hdmi_status','socket_status_updated',)
    actions = ['hdmi_cec_off', 'hdmi_cec_on','reboot_device','exit_socket_app','relaunch_kiosk_browser']
    def hdmi_cec_on(self, request, queryset):
        from .consumers import open_socket_connections
        
        for tv_device in queryset:
            if tv_device.device_id in open_socket_connections and open_socket_connections[tv_device.device_id] is not None:
                sock = open_socket_connections.get(tv_device.device_id)
                sock.send(text_data=json.dumps({
                    'type': 'command',
                    'command': 'hdmi_cec_on'
                }))
                # request.user.message_set.create(message="HDMI CEC turned on for %s" % tv_device.name)
                messages.add_message(request, messages.INFO, 'HDMI CEC turned on for %s (%d)' % (tv_device.name, tv_device.id))
            else:
                # request.user.message_set.create(message="Device %s is not connected" % tv_device.name)
                messages.add_message(request, messages.WARNING, 'Device %s (%d) is not connected' % (tv_device.name, tv_device.id))
    hdmi_cec_on.short_description = "Turn on HDMI CEC"
    
    def hdmi_cec_off(self, request, queryset):
        from .consumers import open_socket_connections
        
        for tv_device in queryset:
            if tv_device.device_id in open_socket_connections and open_socket_connections[tv_device.device_id] is not None:
                sock = open_socket_connections.get(tv_device.device_id)
                sock.send(text_data=json.dumps({
                    'type': 'command',
                    'command': 'hdmi_cec_off'
                }))
                # request.user.message_set.create(message="HDMI CEC turned off for %s" % tv_device.name)
                messages.add_message(request, messages.INFO, 'HDMI CEC turned off for %s (%d)' % (tv_device.name, tv_device.id))
            else:
                # request.user.message_set.create(message="Device %s is not connected" % tv_device.name)
                messages.add_message(request, messages.WARNING, 'Device %s (%d) is not connected' % (tv_device.name, tv_device.id))
    hdmi_cec_off.short_description = "Turn off HDMI CEC"
    
    def reboot_device(self, request, queryset):
        from .consumers import open_socket_connections
        
        for tv_device in queryset:
            if tv_device.device_id in open_socket_connections and open_socket_connections[tv_device.device_id] is not None:
                sock = open_socket_connections.get(tv_device.device_id)
                sock.send(text_data=json.dumps({
                    'type': 'command',
                    'command': 'reboot'
                }))
                # request.user.message_set.create(message="Rebooted %s" % tv_device.name)
                messages.add_message(request, messages.INFO, 'Rebooted %s (%d)' % (tv_device.name, tv_device.id))
            else:
                # request.user.message_set.create(message="Device %s is not connected" % tv_device.name)
                messages.add_message(request, messages.WARNING, 'Device %s (%d) is not connected' % (tv_device.name, tv_device.id))
    reboot_device.short_description = "Reboot device"
    
    def exit_socket_app(self, request, queryset):
        from .consumers import open_socket_connections
        
        for tv_device in queryset:
            if tv_device.device_id in open_socket_connections and open_socket_connections[tv_device.device_id] is not None:
                sock = open_socket_connections.get(tv_device.device_id)
                sock.send(text_data=json.dumps({
                    'type': 'command',
                    'command': 'exit'
                }))
                # request.user.message_set.create(message="Exited socket app on %s" % tv_device.name)
                messages.add_message(request, messages.INFO, 'Exited socket app on %s (%d)' % (tv_device.name, tv_device.id))
            else:
                # request.user.message_set.create(message="Device %s is not connected" % tv_device.name)
                messages.add_message(request, messages.WARNING, 'Device %s (%d) is not connected' % (tv_device.name, tv_device.id))
    exit_socket_app.short_description = "Exit socket app"
    
    def relaunch_kiosk_browser(self, request, queryset):
        from .consumers import open_socket_connections
        
        for tv_device in queryset:
            if tv_device.device_id in open_socket_connections and open_socket_connections[tv_device.device_id] is not None:
                sock = open_socket_connections.get(tv_device.device_id)
                sock.send(text_data=json.dumps({
                    'type': 'command',
                    'command': 'relaunch_kiosk_browser'
                }))
                # request.user.message_set.create(message="Relaunched kiosk browser on %s" % tv_device.name)
                messages.add_message(request, messages.INFO, 'Relaunched kiosk browser on %s (%d)' % (tv_device.name, tv_device.id))
            else:
                # request.user.message_set.create(message="Device %s is not connected" % tv_device.name)
                messages.add_message(request, messages.WARNING, 'Device %s (%d) is not connected' % (tv_device.name, tv_device.id))
    relaunch_kiosk_browser.short_description = "Relaunch kiosk browser"
admin.site.register(PiDevice, PiDeviceAdmin)