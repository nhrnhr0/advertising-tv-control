from typing import Iterable, Optional
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from jsonfield import JSONField
from django.conf import settings
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from server.settings.secrects import FRONTEND_BASE_URL

from server.telegram_bot_interface import send_admin_message
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from server.settings.secrects import BASE_MY_DOMAIN
class Broadcast(models.Model):
    # defult name is the media file name
    name = models.CharField(max_length=100, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='broadcasts/', blank=True, null=True)
    media_type = models.CharField(max_length=100, blank=True, null=True)
    history = JSONField(default=list, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    publisher = models.ForeignKey('core.Publisher', on_delete=models.CASCADE, blank=True, null=True, related_name='broadcasts')

    def get_my_tvs_qs(self):
        return self.broadcast_in_tv.all().order_by('tv')
    
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
            elif media_type == 'jpg' or media_type == 'png' or media_type == 'jpeg' or media_type == 'svg' or media_type == 'webp':
                self.media_type = 'image'
            else:
                # self.media_type = 'unknown'
                raise Exception('unknown media type: ' + self.media.url)
        return super().save(*args, **kwargs)

    def get_tv_display_demo_url(self):
        # http://localhost:5173/publisher/broadcast/27/demo
        return f'{FRONTEND_BASE_URL}/publisher/broadcast/{self.id}/demo'


from polymorphic.models import PolymorphicModel

BROADCAST_SCHEDULE_TYPES = (('plays_countdown', 'ספירת שידורים לאחור'),
                            ('between_dates', 'בין תאריכים'),
                            ('manual_control', 'שליטה ידנית'))
BROADCAST_SCHEDULE_TYPES_DICT = dict(BROADCAST_SCHEDULE_TYPES)
class BroadcastInTvsSchedule(PolymorphicModel):
    content_type = models.CharField(choices=BROADCAST_SCHEDULE_TYPES, max_length=100)
    is_active_var = models.BooleanField(default=False)
    # abstract methods:
    def broadcast_played(self, tv, broadcast):
        # TODO: continue from here
        print('broadcast_played, should be implemented in child class')
        pass
    
    def is_active(self):
        return False
    
    def __str__(self) -> str:
        return f'{BROADCAST_SCHEDULE_TYPES_DICT[self.content_type]}'
    
    def render_schedule(self):
        
        pass
    pass

    def get_data():
        return {}
    
    # save: every save we set is_active_bool based on is_active()
    def save(self, *args, **kwargs):
        self.is_active_var = self.is_active()
        return super().save(*args, **kwargs)

class PlaysCoutdownSchedule(BroadcastInTvsSchedule):
    plays_left = models.IntegerField(default=0)
    telegram_notification_in = models.IntegerField(default=0)
    telegram_notification_sent = models.BooleanField(default=False)
    def need_to_send_telegram_notification(self):
        if self.plays_left <= self.telegram_notification_in and not self.telegram_notification_sent:
            return True
        return False
    def broadcast_played(self, tv, broadcast):
        self.plays_left -= 1
        if self.need_to_send_telegram_notification():
            self.send_telegram_notification()
        self.save()
    def send_telegram_notification(self):
        # TODO: send telegram notification
        return False
    def is_active(self):
        return self.plays_left > 0
    
    def __str__(self) -> str:
        return super().__str__() + f' {self.plays_left}'
    pass

    def get_data(self):
        return {
            'plays_left':self.plays_left,
            'telegram_notification_in':self.telegram_notification_in,
            'telegram_notification_sent':self.telegram_notification_sent,
        }

class BetweenDateSchedule(BroadcastInTvsSchedule):
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField()
    telegram_notification_in = models.DateTimeField(null=True, blank=True)
    telegram_notification_sent = models.BooleanField(default=False)
    def is_active(self):
        now = timezone.now()
        if self.start_date != None:
            import pytz
            aware_start_date = self.start_date.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            aware_end_date = self.end_date.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            if aware_start_date < now and now < aware_end_date:
                return True
        elif self.end_date > now:
            return True
        return False
    def need_to_send_telegram_notification(self):
        # TODO: check that code
        if self.end_date <= timezone.now() and not self.telegram_notification_sent:
            return True
        return False
    def send_telegram_notification(self):
        pass
    def broadcast_played(self, tv, broadcast):
        if self.need_to_send_telegram_notification():
            self.send_telegram_notification()
        pass
    
    def get_data(self):
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'telegram_notification_in': self.telegram_notification_in,
            'telegram_notification_sent': self.telegram_notification_sent,
        }
    pass
    def __str__(self) -> str:
        return super().__str__() + f' {self.start_date} - {self.end_date}'

class ManualControlSchedule(BroadcastInTvsSchedule):
    is_active_bool = models.BooleanField(default=False)
    def is_active(self):
        return self.is_active_bool

    def __str__(self) -> str:
        return super().__str__() + f' {self.is_active_bool}'
    pass
    def broadcast_played(self, tv, broadcast):
        pass
    def get_data(self):
        return {
            'is_active_bool':self.is_active_bool
        }

class BroadcastInTvs(models.Model):
    tvs = models.ManyToManyField(to='Tv')
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='broadcast_in_tvs')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=20.0)
    order = models.IntegerField(default=10)
    master = models.BooleanField(default=False)
    activeSchedule = models.ForeignKey(to=BroadcastInTvsSchedule, on_delete=models.SET_DEFAULT, default=None, null=True, blank=True, related_name='broadcast_in_tvs')
    
    class Meta:
        ordering = ['order', '-created',]
    pass
class BroadcastInTv(models.Model):
    tv = models.ForeignKey('Tv', on_delete=models.CASCADE)
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='broadcast_in_tv')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=20.0)
    order = models.IntegerField(default=10)
    active = models.BooleanField(default=True)
    master = models.BooleanField(default=False)
    plays_left = models.IntegerField(default=0)
    telegram_notification_in = models.IntegerField(default=0)
    telegram_notification_sent = models.BooleanField(default=False)
    enable_countdown = models.BooleanField(default=True)
    
    def get_broadcasts_history(self):
        ret = self.broadcast.history
        # filter by tv
        ret = [x for x in ret if x['tv_id'] == self.tv.id]
        return ret
    
    # def get_absolute_url(self):
    #     return f"/tv/{self.tv.id}/broadcast/{self.id}"
    
    def plays_left_for_notification(self):
        return self.plays_left - self.telegram_notification_in
    
    def __str__(self):
        return f'{self.broadcast.name}: {self.duration}'
    class Meta:
        ordering = ['order', '-created',]
        
    # unused code: TODO: remove it
    def need_to_send_telegram_notification(self):
        if self.plays_left <= self.telegram_notification_in and not self.telegram_notification_sent:
            return True
        return False
    def send_telegram_notification(self):
        
        callback_data_broadcast_reminder_half = json.dumps({'action':'notification_half','id':self.id})
        callback_data_broadcast_reminder_0 = json.dumps({'action':'notification_0','id':self.id})
        callback_data_broadcast_reminder_multiply = json.dumps({'action':'notification_multiply','id':self.id})
        
        send_admin_message(f'שידור <b>{self.broadcast.name}</b> בטלוויזיה <b>{self.tv.name}</b> יפוג בעוד <b>{self.plays_left}</b> שידורים. \n<a href="{BASE_MY_DOMAIN}{self.tv.get_dashboard_url()}">לטלוויזיה</a>',reply_markup=
                           InlineKeyboardMarkup([[
                               InlineKeyboardButton(
                                      text="הזכר לי בחצי" ,
                                        callback_data=callback_data_broadcast_reminder_half
                                 ),
                                InlineKeyboardButton(
                                      text="הזכר לי ב0" ,
                                        callback_data=callback_data_broadcast_reminder_0
                                 ),
                                InlineKeyboardButton(
                                        text="הכפל כמות שידורים" ,
                                        callback_data=callback_data_broadcast_reminder_multiply
                                    ),
                            ]]), parse_mode=ParseMode.HTML,asset=self.broadcast.media,asset_type=self.broadcast.media_type)
        self.telegram_notification_sent = True
    


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
    # location = models.JSONField(blank=True, null=True)
    manual_turn_off = models.BooleanField(default=False)
    location= JSONField(max_length=200, blank=True, null=True)
    buisness_types = models.ManyToManyField(BusinessType, blank=True, related_name='tvs', verbose_name=_('Business type'))
    logo = models.ImageField(upload_to='tv-logos/', blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, verbose_name=_('Phone'), default='0')
    email = models.CharField(max_length=100, blank=True, verbose_name=_('Email'), default='A@A.com')
    contact_name = models.CharField(max_length=100, blank=True, verbose_name=_('Contact name'), default='-')
    contact_phone = models.CharField(max_length=100, blank=True, verbose_name=_('Contact phone'), default='0')
    not_to_show_list = models.ManyToManyField(ContentWithHistory, blank=True, related_name='not_to_show_list')
    yes_to_show_list = models.ManyToManyField(ContentWithHistory, blank=True, related_name='yes_to_show_list')
    web_link = models.CharField(max_length=255, blank=True)
    # opening hours - connected from core.models.TvOpeningHours
    pi = models.OneToOneField('pi.PiDevice', on_delete=models.CASCADE, blank=True, null=True, related_name='tv')
    broadcasts = models.ManyToManyField(Broadcast, blank=True, related_name='tv', through='BroadcastInTv')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    uri_key = models.CharField(max_length=100, blank=True, null=True)
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ['-order','-created',]
    def get_location_json(self):
        return self.location or {}
    # every tv need to keep track of the url visitors. seposed to be only one visitor per tv (this is the busines place) but cloud be more incase someone else go to the url
    # so also keep log, and track of the user's device info
    # pings_log = models.ManyToManyField('PingLog', related_name='pings_log', blank=True)
    def get_tv_display_demo_url(self):
        # localhost:5173/tv-display/1/demo?inactive=true
        return f"{FRONTEND_BASE_URL}/tv-display/{self.id}/demo"
    def get_tv_display_demo_url_with_inactive(self):
        return f"{FRONTEND_BASE_URL}/tv-display/{self.id}/demo?inactive=true"
    
    def get_absolute_url(self):
        return f"/tv/{self.id}"
    def __str__(self):
        return self.name
    def get_dashboard_url(self):
        return f"/dashboard/tvs/{self.id}/"
    def is_in_opening_hours(self,time):
        # 1 - sunday, 2 - monday, 3 - tuesday, 4 - wednesday, 5 - thursday, 6 - friday, 7 - saturday
        weekday = (time.weekday() + 2)%7
        if self.opening_hours.filter(weekday=weekday, from_hour__lte=time.time(), to_hour__gte=time.time()).exists():
            return True
        return False
    
    def get_display_url_with_key(self):
        url = f"{FRONTEND_BASE_URL}/tv-display/{self.id}/"
        if self.uri_key:
            url = f"{url}?key={self.uri_key}"
        return url
    
    def is_opening_hours_active(self):
        if self.manual_turn_off:
            return False
        now = timezone.localtime(timezone.now())
        # 1 - sunday, 2 - monday, 3 - tuesday, 4 - wednesday, 5 - thursday, 6 - friday, 7 - saturday
        weekday = (now.weekday() + 2)%7
        # print('day: ', weekday, 'time: ', now.time())
        # print(self.name, ' opening hours: ', self.opening_hours.count())
        # for i in self.opening_hours.all():
        #     print(i.weekday, i.from_hour, i.to_hour)
        if self.opening_hours.filter(weekday=weekday, from_hour__lte=now.time(), to_hour__gte=now.time()).exists():
            return True
        return False
    
    def get_active_broadcast_to_total_str(self):
        return f'{self.active_broadcasts().count()}/{self.get_broadcasts().count()}'
    
    def active_broadcasts(self):
        return self.broadcasts.filter(broadcast_in_tv__active=True)
        # return empty queryset
        # return self.broadcasts.none()
    
    def inactive_broadcasts(self):
        return self.broadcasts.filter(broadcast_in_tv__active=False)
    
    def get_broadcasts(self):
        return self.broadcasts.all()
        # return empty queryset
        # return self.broadcasts.none()
    
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
    
    def pi__humanize_socket_status_updated_ago(self):
        if self.pi:
            return self.pi.humanize_socket_status_updated_ago()
        else:
            return 'Not set'
    pi__humanize_socket_status_updated_ago.short_description = 'last update'

class playedBroadcast(models.Model):
    uuid = models.CharField(max_length=100, blank=True, null=True,)
    tv = models.ForeignKey(Tv, on_delete=models.SET_NULL, blank=True, null=True)
    broadcast = models.ForeignKey(Broadcast, on_delete=models.SET_NULL, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    uri_key = models.CharField(max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    class Meta:
        ordering = ['-time']
        unique_together = ('uuid', 'tv', 'broadcast', 'time')
    def __str__(self):
        return f'{self.tv.name}: {self.broadcast.name} - {self.time}'
    
    
class AdvertisingAgency(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)
    geojson = JSONField(blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, verbose_name=_('Phone'))
    email = models.CharField(max_length=100, blank=True, verbose_name=_('Email'))
    contact_name = models.CharField(max_length=100, blank=True, verbose_name=_('Contact name'))
    contact_phone = models.CharField(max_length=100, blank=True, verbose_name=_('Contact phone'))
    logo = models.ImageField(upload_to='adv-agens-logos/', blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name