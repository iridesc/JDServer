from django.db import models
import time
# Create your models here.


class TryActivity(models.Model):
    ActivityId=models.IntegerField(db_index=True)
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
    ShopId = models.IntegerField(db_index=True)
    ShopnName = models.CharField(max_length=50)
    LastGotTime = models.FloatField(default=time.time())
 

    





#   # 活动属性提取
#         iteminfo['activityid'] = activity_id
#         iteminfo['trialSkuId'] = data['trialSkuId']
#         iteminfo['startTime'] = data['startTime']/1000
#         iteminfo['endTime'] = data['endTime']/1000
#         iteminfo['supplyCount'] = data['supplyCount']
#         iteminfo['trialName'] = data['trialName']
#         try:
#             iteminfo['shopname'] = data['shopInfo']['title']
#             iteminfo['shopId'] = data['shopInfo']['shopId']
#         except TypeError:
#             print('TypeError when get activity {} shop info '.format(
#                 iteminfo['activityid']))
#             iteminfo['shopname'] = ''
#             iteminfo['shopId'] = ''

#         # 获取价格
#         try:
#             price = get_price(iteminfo)
#         except Exception as e:
#             print(' in {} .\n{}'.format('get_price',str(e)))
#             price = 25
#         iteminfo['price'] = float(price)
