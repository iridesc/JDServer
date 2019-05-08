from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseNotAllowed,HttpResponseBadRequest#引入响应类
import json,time,pytz
from api.models import TryActivity,Shop
from datetime import datetime 


# Create your views here.

# 店铺优惠检查间隔时间（天）
ShopCheckGap = 15
# 随机检查模式每次返回的店铺数量
RandomCheckShopAmount = 50
# 最大获取最近活跃的店铺数量
MaxRecentGotShopAmount = 3000



def distributor(request):
    # try:
        data=json.loads(request.body)
        print('\n-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
        Reason=data['Reason']
        print('Shop Amount:',Shop.objects.all().count(),)
        print('TryActivity Amount:',TryActivity.objects.all().count(),)
        print(Reason)
        if Reason == 'GetTryData':
            return_data=GetTryData(data)
        elif Reason == 'GetBeanData':
            return_data=GetBeanData(data)
        elif Reason == 'UpdateTryData':
            return_data=UpdateTryData(data)
        elif Reason == 'UpdateBeanData':
            return_data=UpdateBeanData(data)
        elif Reason == 'AddBeanData':
            return_data=AddBeanData(data)
        elif Reason == 'Operator':
            return_data=Operator(data)
        elif Reason == 'RemoveExistingActivityId':
            return_data=RemoveExistingActivityId(data)
        elif Reason == 'GetShopsId':
            idlist=[]
            for shop in Shop.objects.all():
                idlist.append(shop.ShopId)
            return_data={
                'ShopIdList':idlist
            }
        
        else:
            return_data={
                'Status':False,
                'Reason':'Unknow optation'
                }
        print('Done .')
    # except Exception as e:
        # print(str(e))
        return_data={
            'Status':False,
            'Reason':'what you want?'
            }

        return JsonResponse(return_data)

def GetTryData(data):
    # 删除过期的
    timeout_activity=TryActivity.objects.filter(EndTime__lt=time.time())
    print('delete:',timeout_activity.count())
    timeout_activity.delete()

    # 获取trydata最后一次更新时间
    last_update_time = TryActivity.objects.order_by('-UpdateTime')[0].UpdateTime
   
    # 当日零时的时间戳
    today_zero_time = datetime.now().replace(hour=8, minute=0, second=0,microsecond=0).timestamp()

    # 判断是否需要爬取
    if (last_update_time<time.time()-12*3600) or ((time.time() > today_zero_time) and (last_update_time<today_zero_time)):
        return_data={
            'Status':False,
            'Reason':'TryDataTimeout'
        }
    else:
        return_data={
            'Status':True
        }
    
    # 选出要当日要结束的活动
    activity_list=list(
            TryActivity.objects.filter(EndTime__gt=time.time())\
                .filter(EndTime__lt=today_zero_time+data['Days']*24*3600)\
                    .values()
        )
    return_data['TryActivityList']=activity_list
    print('return activity amount:',len(activity_list))
    return return_data

def UpdateTryData(data):

    shop_list=[]

    n=0
    for activity in data['TryActivityList']:
    
        # 将合适的店铺加入要储存的店铺列表
        shop_list.append(
                        {
                            'ShopName':activity['ShopName'],
                            'ShopId':activity['ShopId'],
                        }
                    )

        # 更新活动或者创建活动    
        t,created=TryActivity.objects.update_or_create(
            ActivityId=activity['ActivityId'],
            TrialSkuId=activity['TrialSkuId'],
            StartTime=activity['StartTime'],
            EndTime=activity['EndTime'],
            SupplyCount=activity['SupplyCount'],
            TrialName=activity['TrialName'],
            ShopName=activity['ShopName'],
            ShopId=activity['ShopId'],
            Price=activity['Price'],
            )
        if created:
            n+=1

        

  

    # 将相关的店铺存入数据库
    bean_return=AddBeanData({
            'Reason':'AddBeanData',
            'ShopList':shop_list,
            })

    # 返回数据
    return_data={
        'Status':True,
        'SavedAmount':n,
        'AllAmount':len(data['TryActivityList']),
        'AboutBean':bean_return,
    }
    print(return_data)
    
    return return_data

def RemoveExistingActivityId(data):
    activity_id_list=data['ActivityIdList']
    
    new_activity_id_list=[]
    for activity_id in activity_id_list:
        if not TryActivity.objects.filter(ActivityId=activity_id).exists():
            new_activity_id_list.append(activity_id)

    return_data={
        'Status':True,
        'ActivityIdList':new_activity_id_list #[0:50]
    }
    print(len(activity_id_list),' -> ',len(new_activity_id_list),)
    return return_data


def GetBeanData(data):
    if data['Days'] == 0:
        # 在ShopCheckGap天以内没有优惠的店铺中随机选取一部分返回
        shop_for_check_set = Shop.objects.filter(
            LastCheckTime__lt=time.time()-ShopCheckGap*24*3600
            ).order_by('?')[0:RandomCheckShopAmount]

        # 更新最后一次检查时间
        LastCheckTime=time.time()
        for shop in shop_for_check_set:
            shop.LastCheckTime=LastCheckTime

        Shop.objects.bulk_update(shop_for_check_set,['LastCheckTime'])

    else:
        # 选择请求天数以内找优惠活动的店铺
        shop_for_check_set = Shop.objects.filter(
            LastGotTime__gt=time.time()-data['Days']*24*3600
            ).order_by('?')[0:MaxRecentGotShopAmount]

    # 获取shop_list
    shop_list=list(
                    shop_for_check_set.values()
                )
  
    return_data={
        'Status':True,
        'ShopList':shop_list
    }

    return return_data

def AddBeanData(data):
    shop_list=data['ShopList']
    n=0
    for shop in shop_list:
        try:
            s,created=Shop.objects.update_or_create(ShopId=shop['ShopId'],ShopName = shop['ShopName'])
            if created:
                n+=1
        except Exception as e:
            print(e)

    return_data={
        'Status':True,
        'SavedAmount':n,
    }
    print(return_data)
    return return_data

def UpdateBeanData(data):
    shop_list=data['ShopIdList']
    
    n=0
    LastGotTime=time.time()
    ready_for_save_list=[]
    for shop_id in shop_list:
        try:
            s=Shop.objects.get(ShopId=shop_id) 
            s.LastGotTime=LastGotTime         
            ready_for_save_list.append(s)
            n+=1
        except Exception as e:
                print(str(e))
    
    Shop.objects.bulk_update(ready_for_save_list,['LastGotTime'])

    return_data={
        'Status':True,
        'UpdatedAmount':n,
        'AllAmount':len(shop_list),
    }

    print(return_data)

    return return_data



def Operator(data):
    # data={
    #     'Reason':'Operator'
    #     'Password':''
    # }
    if data['Password']=='Irid#1231':
        TryActivity.objects.all().delete()
        Shop.objects.all().delete()
        return_data={
            'Status':True,
        }
    else:
        return_data={
            'Status':False,
            'Reason':'Promission Denied！'
        }
    return return_data

