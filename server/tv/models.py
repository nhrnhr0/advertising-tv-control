from typing import Iterable, Optional
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from jsonfield import JSONField
from django.conf import settings
import json
from django.db.models import Q
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
    def get_active_spots(self, now=None):
        # filter is_active_toggel=True and is_filler=False, and if there is start_at and end_at, check if now is in the range and priceing_plan is not null
        if not now:
            # set to now based on django timezone
            now = timezone.now()
        ret = self.spots.filter(Q(is_active_toggel=True) & Q(is_filler=False) & (Q(start_at__isnull=True) | Q(start_at__lte=now)) & (Q(end_at__isnull=True) | Q(end_at__gte=now)) & Q(priceing_plan__isnull=False))
        return ret
    def get_active_filler_spots(self, now=None):
        # filter is_active_toggel=True and is_filler=True, and if there is start_at and end_at, check if now is in the range and priceing_plan can be null
        if not now:
            # set to now based on django timezone
            now = timezone.now()
        ret = self.spots.filter(Q(is_active_toggel=True) & Q(is_filler=True) & (Q(start_at__isnull=True) | Q(start_at__lte=now)) & (Q(end_at__isnull=True) | Q(end_at__gte=now)))
        return ret
    
    def get_lcm_and_packs(self, spots):
        if(len(spots) < 1):
            return 10, []
        import numpy as np
        workday_minutes = 12 * 60
        pack_list = list(spots.values_list('priceing_plan__name','priceing_plan__plays_per_day','priceing_plan__play_duration',).distinct())
        # [(packing_name, plays_per_day, play_duration),...]
        display_every_x_min_list = []
        packs = []
        for pack in pack_list:
            val = int(workday_minutes / pack[1]) #  pack[1] = plays_per_day
            # pack['display_every_x_min'] = val
            display_every_x_min_list.append(val)
            packs.append({
                'name': pack[0],
                'plays_per_day': pack[1],
                'play_duration': pack[2],
                'display_every_x_min': val,
            })
        
        lcm = np.lcm.reduce(display_every_x_min_list)
        
        for pack in packs:
            pack['multiplier'] = lcm // pack['display_every_x_min']
            
        
        # create a fast access object for the packs
        packs_dict = {}
        for pack in packs:
            packs_dict[pack['name']] = pack
        return lcm, packs_dict
    
    def get_loop_without_fillers(self, spots = None):
        if not spots:
            spots = self.get_active_spots()
        lcm, packs_dict = self.get_lcm_and_packs(spots)
        # packs_dict = {pack['name']: pack for pack in packs}
        loop = []
        # iterate over the spots, and add them to the list according thir pack's multiplier
        for spot in spots:
            pack = packs_dict[spot.priceing_plan.name]
            loop += [spot] * pack['multiplier']
        print(loop)
        return lcm, loop
    
    def get_loop_with_fillers(self, spots = None):
        if not spots:
            spots = self.get_active_spots()
        # lcm, loop_without_fillers = self.get_loop_without_fillers(spots)
        lcm, packs_dict = self.get_lcm_and_packs(spots)
        wanted_loop_duration = lcm * 60
        # get the fillers
        fillers = self.get_active_filler_spots()
        
        current_loop_in_seconds = 0
        for spot in spots:
            pack = packs_dict[spot.priceing_plan.name]
            current_loop_in_seconds += pack['play_duration'] * pack['multiplier']
        
        fillers_amount = self.get_fillers_amount(fillers, wanted_loop_duration - current_loop_in_seconds)
        spot_id_to_spot = {}
        amounts = {}
        for filler in fillers:
            amounts[filler.id] = fillers_amount[filler.id]
            spot_id_to_spot[filler.id] = filler
        
        for spot in spots:
            pack = packs_dict[spot.priceing_plan.name]
            amounts[spot.id] = pack['multiplier']
            spot_id_to_spot[spot.id] = spot
        
        print(amounts)
        spots_ids_list = Tv.spread_spots(amounts)
        print(spots_ids_list)
        
        ret = []
        for spot_id in spots_ids_list:
            ret.append(spot_id_to_spot[spot_id])
        
        return ret
    def spread_spots(broadcasts):
        # Example usage
        # broadcasts = {'A': 10,'B':12, 'C':5, 'D': 2}
        # spread_list = spread_spots(broadcasts) #['B', 'A', 'B', 'A', 'B', 'C', 'A', 'B', 'A', 'B', 'C', 'A', 'B', 'A', 'B', 'D', 'A', 'B', 'C', 'A', 'B', 'A', 'B', 'C', 'A', 'B', 'C', 'B', 'D']
        # print(spread_list)
        # print(len(spread_list))
        broadcast_list = []
        total_items = sum(broadcasts.values())

        for key, value in broadcasts.items():
            broadcasts[key] = {'amount': value, 'show_every_n': total_items / value, 'last_shown': total_items / value}
        
        # we sort the broadcasts by show_every_n
        broadcasts = list(broadcasts.items())
        done = False
        last_inserted = None
        while done == False:
            # reorder based on amount
            # broadcasts = list(sorted(broadcasts, key=lambda x: x[1]['amount']))
            
            # get the last_shown index with the lowest value that amount is not 0
            min_last_shown = 100000
            min_last_shown_index = 100000
            min_last_shown_amount = -1
            for i in range(len(broadcasts)):
                if broadcasts[i][1]['amount'] != 0 and last_inserted != broadcasts[i][0]:
                    if min_last_shown > broadcasts[i][1]['last_shown']:
                        min_last_shown_amount = broadcasts[i][1]['amount']
                        min_last_shown = broadcasts[i][1]['last_shown']
                        min_last_shown_index = i
                    elif min_last_shown == broadcasts[i][1]['last_shown'] and min_last_shown_amount < broadcasts[i][1]['amount']:
                        min_last_shown_amount = broadcasts[i][1]['amount']
                        min_last_shown = broadcasts[i][1]['last_shown']
                        min_last_shown_index = i
            if min_last_shown_index == 100000:
                # find the first one that is not amount = 0
                last_try = False
                for i in range(len(broadcasts)):
                    if broadcasts[i][1]['amount'] != 0:
                        min_last_shown_index = i
                        last_try = True
                        break
                if last_try == False:
                    done = True
                    break
                
            # print('inserting broadcast: ', broadcasts[min_last_shown_index][0])
            # we add the broadcast to the list
            broadcast_list.append(broadcasts[min_last_shown_index][0])
            # we set the last_inserted to the current broadcast
            last_inserted = broadcasts[min_last_shown_index][0]
            # update the last_shown value of all the broadcasts except the current one
            broadcasts[min_last_shown_index][1]['last_shown'] = broadcasts[min_last_shown_index][1]['show_every_n']
            for i in range(len(broadcasts)):
                # if i != min_last_shown_index:
                broadcasts[i][1]['last_shown'] -= 1
                if(broadcasts[i][1]['last_shown'] < 0):
                    broadcasts[i][1]['last_shown'] = 0

            # we decrease the amount of the broadcast
            broadcasts[min_last_shown_index][1]['amount'] -= 1
                

        return broadcast_list
            

    

    
    def get_fillers_amount(self, fillers, max_duration):
        l = self.fill_loop([],fillers, max_duration)
        # iterate over the list and count the fillers
        ret = {}
        for spot in l:
            if spot.id in ret:
                ret[spot.id] += 1
            else:
                ret[spot.id] = 1
        return ret
    
    def mix_loop(self, loop):
        mixed_ids = Tv.rearrangeArray(loop, len(loop))
        arr = list(Spot.objects.filter(id__in=mixed_ids))
        spots_dict = {spot.id: spot for spot in arr}
        loop2 = []
        for id in mixed_ids:
            loop2.append(spots_dict[id])
        return loop2
        pass
    
    
    
    
    def conv(arr):
        return arr.id
    def rearrangeArray(arr, N) :
        # Store frequencies of all elements
        # of the array
        conv = Tv.conv
        mp = {}
        visited = {}    
        for i in range(N) :
            if(conv(arr[i]) in mp) :
                mp[conv(arr[i])] += 1
            else :
                mp[conv(arr[i])] = 1
        
        pq = []
        
        # Adding high freq elements
        # in descending order
        for i in range(N) :
            val = conv(arr[i])
            if((val in mp) and ((val not in visited) or (visited[val] != 1))) :
                pq.append([mp[val], val])
            visited[val] = 1   
        pq.sort()
        pq.reverse()
        
        # 'result[]' that will store resultant value
        result = [0]*N
        
        # Work as the previous visited element
        # initial previous element will be ( '-1' and
        # it's frequency wiint also be '-1' )
        prev = [-1, -1]
        l = 0
        
        # Traverse queue
        while (len(pq) != 0) :
            
            # Pop top element from queue and add it
            # to result
            k = pq[0]
            pq.pop(0)
            result[l] = k[1]
            
            # If frequency of previous element is less
            # than zero that means it is useless, we
            # need not to push it
            if (prev[0] > 0) :
            
                pq.append(prev)
                pq.sort()
                pq.reverse()
            
            # Make current element as the previous
            # decrease frequency by 'one'
            prev = [k[0] - 1, k[1]]
            l += 1
            
        for it in result :
            if (it == 0) :
                
                # If found 0, No valid result
                # array possible
                print("Not valid Array")
                return   
        return result
    def fill_loop(self, loop_without_fillers, fillers, max_duration):
        total_duration = 0
        loop = []
        # we need to do the best try to fill the exact time of the loop (max_duration) with the fillers, try to make the fillers even
        # so we will start with the fillers that have the smallest duration
        
        
        # filler_index = 0
        # fillers_added = 0
        # while done == False:
        #     iterate over the fillers, and add them to the loop until the loop is full
        #     done_fillers = False
        #     if total_duration == max_duration:
        #         done = True
        #     else if total_duration > max_duration:
        #         while done_fillers == False:
        #             # remove the last filler from the loop
        #             # aall find_changes
        #             # if found option, add it to the loop and done_fillers = True
        #             # else remove the next filler from the loop and filler_index -= 1
        #             # if no more fillers (fillers_added = 0), done_fillers = True # eage case: should not happen
        #     else:
        #         # add the next filler to the loop (filler_index % len(fillers))
        #         # filler_index += 1
        #         # fillers_added += 1
        for item in loop_without_fillers:
            total_duration += item.get_duration()
            loop.append(item)
        
        filler_index = 0
        fillers_added = 0
        done = False
        while done == False:
            # iterate over the fillers, and add them to the loop until the loop is full
            done_fillers = False
            if total_duration == max_duration:
                done = True
            elif total_duration > max_duration:
                while done_fillers == False:
                    # remove the last filler from the loop
                    item = loop.pop()
                    total_duration -= item.get_duration()
                    time_left_to_fill = max_duration - total_duration
                    # aall find_changes
                    tmp = Tv.find_changes(time_left_to_fill, fillers)
                    # if found option, add it to the loop and done_fillers = True
                    # else remove the next filler from the loop and filler_index -= 1
                    # if no more fillers (fillers_added = 0), done_fillers = True # eage case: should not happen
                    filler_index -= 1
                    fillers_added -= 1
                    if fillers_added == 0:
                        done_fillers = True
                        done = True
            else:
                # add the next filler to the loop (filler_index % len(fillers))
                filler = fillers[filler_index % len(fillers)]
                filler_duration = filler.get_duration()
                total_duration += filler_duration
                loop.append(filler)
                filler_index += 1
                fillers_added += 1
        return loop
        # we use find_changes to find all the possible combinations of fillers that can fill the loop
        # all_options = Tv.find_changes(max_duration, fillers)
        # print(all_options)
    # def find_changes(n, coins):
    #     print('find_changes', n, coins)
    #     if n < 0:
    #         return []
    #     if n == 0:
    #         return [[]]
    #     all_changes = []

    #     for last_used_coin in coins:
    #         current_duration = last_used_coin.filler_duration or (last_used_coin.priceing_plan and last_used_coin.priceing_plan.duration)
    #         combos = Tv.find_changes(n - current_duration, coins)
    #         for combo in combos:
    #             combo.append(last_used_coin)
    #             all_changes.append(combo)

    #     return all_changes
    def find_changes(amount,coins):
        # Dictionary to store memorized solutions for different amounts
        memo = {}
        
        def helper(remaining_amount):
            if remaining_amount == 0:
                return [[]]  # Base case: One way to make zero amount - using no coins
            
            if remaining_amount < 0:
                return []  # Base case: No way to make negative amount
            
            if remaining_amount in memo:
                return memo[remaining_amount]
            
            all_solutions = []
            
            for coin in coins:
                duration = coin.filler_duration or (coin.priceing_plan and coin.priceing_plan.duration)
                sub_solutions = helper(remaining_amount - duration)
                for solution in sub_solutions:
                    new_solution = solution + [coin]
                    all_solutions.append(new_solution)
            
            memo[remaining_amount] = all_solutions
            return all_solutions
        
        ret=  helper(amount)
        return ret
        
        pass
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
    

# new vertion to handle spots (broadcasts) in the tvs:
# model PriceingPlan
class PriceingPlen(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    description = models.TextField(blank=True, null=True)
    plays_per_day = models.IntegerField(default=0)
    play_duration = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
# new every spot can be made from multiple assets
class Asset(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, default='')
    media = models.FileField(upload_to='assets/')
    media_type = models.CharField(max_length=100, blank=True, null=True, default='')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    # on save if there is no name set the name to the file name, and if there is no media_type set it to the file extension
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.media.name.split('/')[-1]
        if not self.media_type:
            url = self.media.url
            media_type = url.split('.')[-1].lower() # video/image
            if media_type == 'mp4':
                self.media_type = 'video'
            elif media_type == 'jpg' or media_type == 'png' or media_type == 'jpeg' or media_type == 'svg' or media_type == 'webp' or media_type == 'gif':
                self.media_type = 'image'
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    

class Spot(models.Model):
    is_active_toggel = models.BooleanField(default=False)
    priceing_plan = models.ForeignKey(PriceingPlen, on_delete=models.SET_NULL, blank=True, null=True)
    assets = models.ManyToManyField(Asset, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    publisher = models.ForeignKey('core.Publisher', on_delete=models.SET_NULL, blank=True, null=True)
    tvs = models.ManyToManyField(Tv, blank=True, related_name='spots')
    
    is_filler = models.BooleanField(default=False)
    filler_duration = models.IntegerField(default=0)
    
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    
    def get_assets_serialize(self):
        ret = []
        for asset in self.assets.all():
            ret.append({
                'id': asset.id,
                'name': asset.name,
                'media': asset.media.url,
                'media_type': asset.media_type,
            })
        return ret
    
    # is_active if is_active_toggel and start_at < now < end_at start_at and end_at are not required
    def is_active(self):
        ret = self.is_active_toggel and (not self.start_at or self.start_at < timezone.now()) and (not self.end_at or self.end_at > timezone.now())
        # if it's not a filler we need to make sure it has a priceing_plan
        if self.is_filler == False:
            ret = ret and self.priceing_plan != None
        return ret
    is_active.boolean = True
    def get_duration(self):
        # if it's a filler we need to return the filler_duration else we need to return the priceing_plan.play_duration
        if self.is_filler:
            return self.filler_duration
        else:
            return self.priceing_plan.play_duration
    def tvs_display(self):
        ret = ""
        ret += "<ol style='margin:0;padding:0;type=\"1\"'>"
        for tv in self.tvs.all():
            ret += "<li style='line-height:1;'><a href='/admin/tv/tv/{}/change/'>{}</a></li>".format(tv.id, tv.name)
        ret += "</ol>"
        return mark_safe(ret)
    pass

    def html_assets_display(self, w=88.888889, h=50):
        ret = ""
        ret += "<div style='display:grid;flex-wrap:wrap;grid-template-columns: repeat(auto-fill, minmax({w}px, 1fr));width:{div_width}px;'>".format(w=w,div_width=w*self.assets.count())
        for asset in self.assets.all():
            if asset.media_type == "video":
                ret += '<video style="outline:1px solid #333;" width="{w}px" height="{h}px" controls><source src="{url}" type="video/mp4"></video>'.format(
                url = asset.media.url,
                w=w,
                h=h
                )
            else:
                ret += '<img style="outline:1px solid #333;" src="{url}" width="{w}px" height="{h}px" />'.format(
                    url = asset.media.url,
                    w=w,
                    h=h
                    )
        ret += "</div>"
        return mark_safe(ret)