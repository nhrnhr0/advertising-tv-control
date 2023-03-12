from django.db import models
from django.utils import timezone
import humanize
from django.utils.safestring import mark_safe
import os
from server.settings.secrects import PI_MONITOR_SERVER_URL
import requests
# from pi.storage import OverwriteStorage
# Create your models here.
def image_path(instance, filename):
    return os.path.join('last_images', str(instance.id), 'image_{}.jpg'.format(timezone.now().strftime('%Y-%m-%d_%H-%M-%S')))


class PiDevice(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    remote_last_image = models.ImageField(upload_to=image_path, blank=True, null=True)  # , storage=OverwriteStorage())
    image_updated = models.DateTimeField(null=True, blank=True)
    socket_status_updated = models.DateTimeField(null=True)
    cec_hdmi_status = models.CharField(max_length=100, default='unknown')
    is_approved = models.BooleanField(default=False)
    telegram_connection_error_sent = models.BooleanField(default=False)
    def get_tv_display_url_with_key(self):
        if self.tv:
            return self.tv.get_display_url_with_key()
        else:
            return ''
        pass
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

    def send_reboot_device(self):
        url = PI_MONITOR_SERVER_URL + '/command/'
        data = {'command': 'reboot', 'device_id': self.device_id}
        r = requests.post(url, data=data)
        return r
    
    def send_cec_off(self):
        url  = PI_MONITOR_SERVER_URL + '/command/'
        data = {'command': 'hdmi_cec_off', 'device_id': self.device_id}
        r = requests.post(url, data=data)
        return r
    
    def send_cec_on(self):
        url  = PI_MONITOR_SERVER_URL + '/command/'
        data = {'command': 'hdmi_cec_on', 'device_id': self.device_id}
        r = requests.post(url, data=data)
        return r
    
    def send_relaunch_kiosk_browser(self):
        url  = PI_MONITOR_SERVER_URL + '/command/'
        data = {'command': 'relaunch_kiosk_browser', 'device_id': self.device_id}
        r = requests.post(url, data=data)
        return r
    
    def send_set_tv_url(self):
        url  = PI_MONITOR_SERVER_URL + '/command/'
        data = {'command': 'set_tv_url', 'device_id': self.device_id, 'url': self.get_tv_display_url_with_key()}
        r = requests.post(url, data=data)
        return r