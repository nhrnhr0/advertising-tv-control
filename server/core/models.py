from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField

class PublisherType(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

# from tv.models import Broadcast
# Create your models here.
class Publisher(models.Model):
    # usr  = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    # )
    name = models.CharField(max_length=100)
    broadcasts = models.ManyToManyField('tv.Broadcast', blank=True, related_name='publisher')
    about = models.TextField(blank=True)
    geojson = JSONField(blank=True, null=True)
    publishers_types = models.ManyToManyField(PublisherType, blank=True, related_name='publishers', verbose_name=_('publishers types'))
    logo = models.ImageField(upload_to='publishers-logos/', blank=True, null=True)
    address = models.CharField(max_length=100, blank=True , verbose_name=_('Address'), default='')
    phone = models.CharField(max_length=100, blank=True, verbose_name=_('Phone'), default='0')
    email = models.CharField(max_length=100, blank=True, verbose_name=_('Email'), default='A@A.com')
    contact_name = models.CharField(max_length=100, blank=True, verbose_name=_('Contact name'), default='איש קשר חסר')
    contact_phone = models.CharField(max_length=100, blank=True, verbose_name=_('Contact phone'), default='0')
    qr_link = models.CharField(max_length=100, blank=True, verbose_name=_('QR link'))
    adv_agency = models.ForeignKey('tv.AdvertisingAgency', on_delete=models.CASCADE, blank=True, null=True, related_name='publishers')
    pass

    def active_broadcasts(self):
        return self.broadcasts.filter(broadcast_in_tv__active=True, broadcast_in_tv__plays_left__gt=0)



# isoweekday
WEEKDAYS = [
    (1, _("Sunday")),
    (2, _("Monday")),
    (3, _("Tuesday")),
    (4, _("Wednesday")),
    (5, _("Thursday")),
    (6, _("Friday")),
    (7, _("Saturday")),
    
]

class TvOpeningHours(models.Model):
    """
    Store opening times of company premises,
    defined on a daily basis (per day) using one or more
    start and end times of opening slots.
    """
    class Meta:
        verbose_name = _('Opening Hours')  # plurale tantum
        verbose_name_plural = _('Opening Hours')
        ordering = ['tv', 'weekday', 'from_hour']
    tv = models.ForeignKey('tv.Tv', on_delete=models.CASCADE, related_name='opening_hours')
    weekday = models.IntegerField(_('Weekday'), choices=WEEKDAYS)
    from_hour = models.TimeField(_('Opening'))
    to_hour = models.TimeField(_('Closing'))
    def get_weekday_display(self):
        return dict(WEEKDAYS)[self.weekday]
    def __str__(self):
        return _("%(weekday)s (%(from_hour)s - %(to_hour)s)") % {
            'weekday': self.get_weekday_display(),
            'from_hour': self.from_hour,
            'to_hour': self.to_hour
        }