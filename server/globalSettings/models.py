from django.db import models

# Create your models here.


class GlobalSettings(models.Model):
    # boolean to turn off all the tvs:
    turn_off_all_tvs = models.BooleanField(default=False)
    # defult opening hours from `tv.GlobalOpeningHours`
    defult_opening_hours = models.ManyToManyField('tv.OpeningHours', blank=True)
    defult_broadcasts = models.ManyToManyField('tv.Broadcast', blank=True)
    
