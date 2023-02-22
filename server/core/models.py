from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# from tv.models import Broadcast
# Create your models here.
class Publisher(models.Model):
    # usr  = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    # )
    name = models.CharField(max_length=100)
    broadcasts = models.ManyToManyField('tv.Broadcast', blank=True, related_name='publisher')
    pass



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

    def __str__(self):
        return _("%(premises)s %(weekday)s (%(from_hour)s - %(to_hour)s)") % {
            'premises': self.tv,
            'weekday': self.weekday,
            'from_hour': self.from_hour,
            'to_hour': self.to_hour
        }