from typing import Iterable, Optional
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Broadcast(models.Model):
    # defult name is the media file name
    name = models.CharField(max_length=100, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='broadcasts/', blank=True, null=True)
    media_type = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ['-created',]
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
    plays_left = models.IntegerField(default=0)
    
    # def get_absolute_url(self):
    #     return f"/tv/{self.tv.id}/broadcast/{self.id}"
    
    def __str__(self):
        return f'{self.broadcast.name}: {self.duration}'
    class Meta:
        ordering = ['order', '-created',]
        


class BusinessType(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class ContentWithHistory(models.Model):
    NOT_TO_SHOW = 'not_to_show'
    YES_TO_SHOW = 'yes_to_show'
    
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ['-created',]
    
    def __str__(self):
        return f'{self.content_type}: {self.content}'

# Create your models here.
class Tv(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)
    location = models.JSONField(blank=True, null=True)
    buisness_types = models.ManyToManyField(BusinessType, blank=True, related_name='tvs', verbose_name=_('Business type'))
    logo = models.ImageField(upload_to='tv-logos/', blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, verbose_name=_('Phone'))
    email = models.CharField(max_length=100, blank=True, verbose_name=_('Email'))
    contact_name = models.CharField(max_length=100, blank=True, verbose_name=_('Contact name'))
    contact_phone = models.CharField(max_length=100, blank=True, verbose_name=_('Contact phone'))
    not_to_show_list = models.ManyToManyField(ContentWithHistory, blank=True, related_name='not_to_show_list')
    yes_to_show_list = models.ManyToManyField(ContentWithHistory, blank=True, related_name='yes_to_show_list')
    web_link = models.CharField(max_length=255, blank=True)
    # opening hours - connected from core.models.TvOpeningHours
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
    
    def is_opening_hours_active(self):
        now = timezone.now()
        if self.opening_hours.filter(weekday=now.weekday(), from_hour__lte=now.time(), to_hour__gte=now.time()).exists():
            return True
        return False
    
    def active_broadcasts(self):
        return self.broadcasts.filter(broadcast_in_tv__active=True)
    
    def inactive_broadcasts(self):
        return self.broadcasts.filter(broadcast_in_tv__active=False)
    
    def get_broadcasts(self):
        return self.broadcasts.all()
    
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