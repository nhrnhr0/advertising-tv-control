from django.db import models

# Create your models here.


class GlobalSettings(models.Model):
    # boolean to turn off all the tvs:
    turn_off_all_tvs = models.BooleanField(default=False)
    # defult opening hours from `tv.GlobalOpeningHours`
    defult_opening_hours = models.ManyToManyField('core.OpeningHours', blank=True)
    defult_broadcasts = models.ManyToManyField('tv.Broadcast', blank=True)
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ['order', '-id']


def get_global_settings():
    # get the global settings
    global_settings = GlobalSettings.objects.all().order_by('order', '-id')
    if global_settings.exists():
        return global_settings.first()
    else:
        return None