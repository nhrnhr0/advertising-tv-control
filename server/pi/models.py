from django.db import models
from django.utils import timezone
from datetime import timedelta
import humanize
from django.utils.safestring import mark_safe
import os
from server.tasks import ALERT_THRESHOLD
import requests
from server.telegram_bot_interface import send_admin_message


# class SocketDeviceIds(models.Model):
#     device_id = models.CharField(max_length=100, unique=True)
#     connections_count = models.IntegerField(default=0)
#     is_approved = models.BooleanField(default=False)
#     date_added = models.DateTimeField(default=timezone.now)



# from pi.storage import OverwriteStorage
# Create your models here.
def image_path(instance, filename):
    return os.path.join('last_images', str(instance.id), 'image_{}.jpg'.format(timezone.now().strftime('%Y-%m-%d_%H-%M-%S')))


class PiDevice(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    remote_last_image = models.ImageField(upload_to=image_path, blank=True, null=True)
    socket_status_updated = models.DateTimeField(null=True)
    cec_hdmi_status = models.TextField(default='unknown')
    group_channel_name = models.CharField(max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    telegram_connection_error_sent = models.BooleanField(default=False)
    image_updated = models.DateTimeField(null=True, blank=True)
    def get_tv_display_url_with_key(self):
        if self.tv:
            return self.tv.get_display_url_with_key()
        else:
            return ''
        pass
    
    def is_socket_connected_live(self):
        return self.group_channel_name is not None
    is_socket_connected_live.short_description = 'socket connected'
    is_socket_connected_live.boolean = True
    
    def socket_info_updated(self):
        # check if socket_status_updated is updated in the last ALERT_THRESHOLD seconds and if so and telegram_connection_error_sent = True then set it to False
        if self.telegram_connection_error_sent:
            self.telegram_connection_error_sent = False
            # send alert
            send_admin_message(f'🟢התקשורת עם המכשיר <b>{self.name}</b> חזר לעבוד כרגיל')
            self.save()
    
    def __str__(self):
        return self.name or self.device_id

    def tv_admin_link(self):
        # /admin/tv/tv/1/change/
        if self.tv:
            return mark_safe(u'<a href="/admin/tv/tv/%s/change/">%s</a>' % (self.tv.id, self.tv))
        else:
            return ''
    def humanize_image_updated_ago(self):
        # in hebrew
        if self.image_updated:
            return humanize.naturaltime(timezone.now() - self.image_updated)
        else:
            return ''

    def humanize_socket_status_updated_ago(self):
        # in hebrew
        return humanize.naturaltime(timezone.now() - self.socket_status_updated)

    humanize_socket_status_updated_ago.short_description = 'socket connection updated'

    def image_tag(self):
        if self.remote_last_image:
            return mark_safe(u'<img src="%s" width="150px" height="150px" />' % self.remote_last_image.url)
        else:
            return ''

    def send_reboot(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_reboot_to_channel
                send_reboot_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def send_refresh_page(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_refresh_page_to_channel
                send_refresh_page_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def send_deploy(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_deploy_to_channel
                send_deploy_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def send_system_update(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_system_update_to_channel
                send_system_update_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def send_hdmi_cec_off(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_hdmi_cec_off_to_channel
                send_hdmi_cec_off_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def send_hdmi_cec_on(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_hdmi_cec_on_to_channel
                send_hdmi_cec_on_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def send_relaunch_kiosk_browser(self):
        try:
            if self.is_socket_connected_live():
                channel_name = self.group_channel_name
                from .consumers import send_relaunch_kiosk_browser_to_channel
                send_relaunch_kiosk_browser_to_channel(channel_name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def send_set_tv_url(self, url=None):
        try:
            if self.is_socket_connected_live():
                if not url:
                    url = self.tv.get_display_url_with_key()
                channel_name = self.group_channel_name
                from .consumers import send_set_tv_url_to_channel
                send_set_tv_url_to_channel(channel_name,url)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False