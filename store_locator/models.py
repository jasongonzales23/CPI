import tarfile
import StringIO
import shutil
import os
import math
from django.conf import settings
from django.db import models
from cms.models import CMSPlugin

class LocationManager(models.Manager):
    def __init__(self):
        super(LocationManager, self).__init__()

    def near(self, source_latitude, source_longitude, distance):
        queryset = super(LocationManager, self).get_query_set()
        rough_distance = distance / 2
        queryset = queryset.filter(
                    latitude__range=(source_latitude - rough_distance, source_latitude + rough_distance), 
                    longitude__range=(source_longitude - rough_distance, source_longitude + rough_distance)
                    )
        locations = []
        for location in queryset:
            if location.latitude and location.longitude:
                exact_distance = self.GetDistance(
                                    source_latitude, source_longitude,
                                    location,
                                    )
                if exact_distance <= distance:
                    setattr(location, 'distance', exact_distance)
                    locations.append(location)
                    #print "%s - %s" % (location, exact_distance)
                    
        return locations
        #queryset = queryset.filter(id__in=[l.id for l in locations])
        #return queryset

    def GetDistance(self, source_latitude, source_longitude, target_location):
        lat_1 = math.radians(source_latitude)
        long_1 = math.radians(source_longitude)
        
        lat_2 = math.radians(target_location.latitude)
        long_2 = math.radians(target_location.longitude)
        
        dlong = long_2 - long_1
        dlat = lat_2 - lat_1
        a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlong / 2))**2
        c = 2 * math.asin(min(1, math.sqrt(a)))
        dist = 3956 * c
        return dist


class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(max_length=255, blank=False)
    latitude = models.FloatField(blank=False, null=True)
    longitude = models.FloatField(blank=False, null=True, help_text="If you do not enter a latitude and longitude we will try to find them for you using Google Maps.")
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    
    objects = LocationManager()

    class Meta:
        verbose_name = "Store Location"
        verbose_name_plural = "Store Locations"

    def __unicode__(self):
        return self.name
    
    def get_single_line_address(self):
        return self.address.replace('\n', ', ')
        
class StoreLocator(CMSPlugin):
    distance = models.IntegerField(default=100)
    
