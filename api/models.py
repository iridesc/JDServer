from django.db import models
import time
# Create your models here.


class TryActivity(models.Model):
    ActivityId=models.IntegerField(primary_key=True, db_index=True)
    TrialSkuId=models.IntegerField()
    StartTime=models.FloatField()
    EndTime=models.FloatField()
    SupplyCount=models.IntegerField()
    TrialName=models.CharField(max_length=200)
    ShopName=models.CharField(max_length=50,default='')
    ShopId=models.IntegerField(default=0)
    Price=models.FloatField()

    UpdateTime =models.FloatField(default=time.time())


class Shop(models.Model):
    LastCheckTime = models.FloatField(default=0)
    ShopId = models.IntegerField(primary_key=True,db_index=True,)
    ShopName = models.CharField(max_length=50)
    LastGotTime = models.FloatField(default=0)
    LastCheckTime = models.FloatField(default=0)
 

    





