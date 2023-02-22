from typing import Iterable, Optional
from django.db import models
from django.utils.safestring import mark_safe


class Broadcast(models.Model):
    # defult name is the media file name
    name = models.CharField(max_length=100, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='broadcasts/', blank=True, null=True)
    media_type = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name or 'error'
    def save(self,*args, **kwargs):
        if not self.name or self.name == '':
            self.name = self.media.name
        if not self.media_type and self.media:
            url = self.media.url
            media_type = url.split('.')[-1].lower() # video/image
            if media_type == 'mp4':
                self.media_type = 'video'
            elif media_type == 'jpg' or media_type == 'png' or media_type == 'jpeg' or media_type == 'gif' or media_type == 'svg' or media_type == 'webp':
                self.media_type = 'image'
            else:
                self.media_type = 'unknown'
        return super().save(*args, **kwargs)




class BroadcastInTv(models.Model):
    tv = models.ForeignKey('Tv', on_delete=models.CASCADE)
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='broadcast_in_tv')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=20.0)
    order = models.IntegerField(default=10)
    active = models.BooleanField(default=True)
    # def get_absolute_url(self):
    #     return f"/tv/{self.tv.id}/broadcast/{self.id}"
    
    def __str__(self):
        return f'{self.broadcast.name}: {self.duration}'
    class Meta:
        ordering = ['order',]
        
# Create your models here.
class Tv(models.Model):
    name = models.CharField(max_length=100)
    pi = models.OneToOneField('pi.PiDevice', on_delete=models.CASCADE, blank=True, null=True, related_name='tv')
    broadcasts = models.ManyToManyField(Broadcast, blank=True, related_name='tv', through='BroadcastInTv')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # every tv need to keep track of the url visitors. seposed to be only one visitor per tv (this is the busines place) but cloud be more incase someone else go to the url
    # so also keep log, and track of the user's device info
    # pings_log = models.ManyToManyField('PingLog', related_name='pings_log', blank=True)
    def get_absolute_url(self):
        return f"/tv/{self.id}"
    def __str__(self):
        return self.name
    
    def pi_admin_link(self):
        if self.pi:
            # /admin/pi/pidevice/?device_id=XXX
            return mark_safe(f'<a href="/admin/pi/pidevice/?device_id={self.pi.device_id}">{str(self.pi)}</a>')
            # return mark_safe(f'<a href="/admin/pi/pidevice/{self.pi.id}">{str(self.pi)}</a>')
        else:
            return 'Not set'
    pi_admin_link.short_description = 'Pi'
    
    
    def pi__cec_hdmi_status(self):
        if self.pi:
            return self.pi.cec_hdmi_status
        else:
            return 'Not set'
    pi__cec_hdmi_status.short_description = 'HDMI'
    def pi__is_socket_connected_live(self):
        if self.pi:
            return self.pi.is_socket_connected_live()
        else:
            return False
    pi__is_socket_connected_live.boolean = True
    pi__is_socket_connected_live.short_description = 'Socket connected'
    def pi__humanize_socket_status_updated_ago(self):
        if self.pi:
            return self.pi.humanize_socket_status_updated_ago()
        else:
            return 'Not set'
    pi__humanize_socket_status_updated_ago.short_description = 'last update'

class playedBroadcast(models.Model):
    uuid = models.CharField(max_length=100, blank=True, null=True, unique=True)
    tv = models.ForeignKey(Tv, on_delete=models.CASCADE)
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-time']
        unique_together = ('uuid', 'tv', 'broadcast', 'time')
    def __str__(self):
        return f'{self.tv.name}: {self.broadcast.name} - {self.time}'