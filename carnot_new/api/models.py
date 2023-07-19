from django.db import models

# Create your models here.
class CarnotTable(models.Model):
    device_fk_id = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    time_stamp = models.DateTimeField()
    sts = models.DateTimeField()
    speed = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.device_fk_id}"
