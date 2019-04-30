from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseNotAllowed,HttpResponseBadRequest#引入响应类
import json,time,pytz
from api.models import TryActivity,Shop
from datetime import datetime 


# Create your views here.

# 
RandomGetShopDaysLimit = 1
#
ShopEachRetuenAmount = 100
#
MaxRecentGotShopAmount=5000






def distributor(request):
    try:
        data=json.loads(request.body)
        Reason=data['Reason']
        print('Shop Amount:',Shop.objects.all().count(),)
        print('TryActivity Amount:',TryActivity.objects.all().count(),)
        
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
    except Exception as e:
        print(str(e))
        return_data={
            'Status':False,
            'Reason':'what you want?'
            }

    return JsonResponse(return_data)



def GetTryData(data):
    print('GetTryData',)
   
    # 获取trydata最后一次更新时间
    last_update_time = TryActivity.objects.order_by('-UpdateTime')[0].UpdateTime
    # 当日零时的时间戳
    today_zero_time = datetime.now().replace(hour=0, minute=0, second=0,microsecond=0).timestamp()+8*3600

    # 判断是否需要爬取
    if last_update_time<time.time()-12*3600 or ((time.time() > today_zero_time) and (last_update_time<today_zero_time)):
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
   
    print('Done .')
    return return_data

def UpdateTryData(data):
    print('UpdateTryData',)

    # 除去重复的活动
    try_activity_list=[]
    unique_check=[]
    for activity in data['TryActivityList']:
        if activity['ActivityId'] not in unique_check:
            unique_check.append(activity['ActivityId'])
            try_activity_list.append(activity)

    ready_for_save_list=[]
    shop_list=[]
    for try_activity in try_activity_list:
        # 将合适的店铺加入要储存的店铺列表
        shop_list.append(
                        {
                            'ShopName':try_activity['ShopName'],
                            'ShopId':try_activity['ShopId'],
                        }
                    )

        # 判断结束时间是否大于当前时间
        if try_activity['EndTime'] > time.time():
            if not TryActivity.objects.filter(ActivityId=try_activity['ActivityId']).exists():
                
                # 将符合条件的加入准备储存列表
                if try_activity['ShopId']=='':
                    ready_for_save_list.append(
                        TryActivity(
                            ActivityId=try_activity['ActivityId'],
                            TrialSkuId=try_activity['TrialSkuId'],
                            StartTime=try_activity['StartTime'],
                            EndTime=try_activity['EndTime'],
                            SupplyCount=try_activity['SupplyCount'],
                            TrialName=try_activity['TrialName'],
                            Price=try_activity['Price'],
                        )
                    )

                else:
                    
                    ready_for_save_list.append(
                        TryActivity(
                            ActivityId=try_activity['ActivityId'],
                            TrialSkuId=try_activity['TrialSkuId'],
                            StartTime=try_activity['StartTime'],
                            EndTime=try_activity['EndTime'],
                            SupplyCount=try_activity['SupplyCount'],
                            TrialName=try_activity['TrialName'],
                            ShopName=try_activity['ShopName'],
                            ShopId=try_activity['ShopId'],
                            Price=try_activity['Price'],
                        )
                    )
                    
                # print('add')
            else:
                # print('activity exist')
                pass
        else:
            # print('activity timeout')
            pass
    # 存入数据库
    TryActivity.objects.bulk_create(ready_for_save_list)

    # 将相关的店铺存入数据库
    bean_return=AddBeanData({
            'Reason':'AddBeanData',
            'ShopList':shop_list,
            })
    
    return_data={
        'Status':True,
        'SavedAmount':len(ready_for_save_list),
        'SavedRate':len(try_activity_list),
        'AboutBean':bean_return,
    }
    print(return_data)
    print('Done .')
    return return_data

def RemoveExistingActivityId(data):
    print('RemoveExistingActivityId',)

    activity_id_list=data['ActivityIdList']
    
    new_activity_id_list=[]
    for activity_id in activity_id_list:
        if not TryActivity.objects.filter(ActivityId=activity_id).exists():
            new_activity_id_list.append(activity_id)

    return_data={
        'Status':True,
        'ActivityIdList':new_activity_id_list
    }
    print(len(activity_id_list),' -> ',len(new_activity_id_list),)
    print('Done .')
    return return_data


def GetBeanData(data):
    print('GetBeanData',)
    if data['Days'] == 0:
        # 在 选择15天以内没有获得的 中 随机选取 50
        shop_list=list(
            Shop.objects.filter(LastGotTime__lt=time.time()-RandomGetShopDaysLimit*24*3600)\
                .order_by('?')[0:ShopEachRetuenAmount]\
                    .values()
            )
    else:
        # 选择15天以内找到活动的
        shop_list=list(Shop.objects.filter(LastGotTime__gt=time.time()-data['Days']*24*3600)
        .order_by('?')\
            [0:MaxRecentGotShopAmount]\
                .values())
    
    return_data={
        'Status':True,
        'ShopList':shop_list
    }

    print('Done .')
    return return_data

def AddBeanData(data):
    print('AddBeanData',)
    shop_list=data['ShopList']
    
    ready_for_save_list=[]
    ready_for_save_shop_id_list=[]
    for shop in shop_list:
        if shop['ShopId']!='':
            if (not Shop.objects.filter(ShopId=shop['ShopId']).exists()) and (shop['ShopId'] not in ready_for_save_shop_id_list):
                ready_for_save_list.append(
                    Shop(
                        ShopId = shop['ShopId'],
                        ShopName = shop['ShopName'],
                    )
                )
                ready_for_save_shop_id_list.append(shop['ShopId'])
            else:
                #print('shop exits')
                pass
    
    Shop.objects.bulk_create(ready_for_save_list)

    return_data={
        'Status':True,
        'SavedAmount':len(ready_for_save_list),
        'SavedRate':len(shop_list),
    }
    print('Done .')
    return return_data

def UpdateBeanData(data):
    print('UpdateBeanData',)

    shop_list=data['ShopList']
    
    n=0
    error_list=[]
    for shop in shop_list:
        if shop['ShopId']!='':
            try:
                s=Shop.objects.get(ShopId=shop['ShopId'])
                if s.LastGotTime < shop['LastGotTime']:
                    s.LastGotTime=shop['LastGotTime']
                    s.save()
                    n+=1
            except Exception as e:
                # print(str(e))
                error_list.append(str(e))  
        else:
            error_list.append('ShopId is Blank')  
    return_data={
        'Status':True,
        'UpdatedAmount':n,
        'TotalRate':len(shop_list),
        'ErrorList':error_list,
    }
    print(return_data)
    print('Done .')
    return return_data



def Operator(data):
    print('Operator',)

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
    print('Done .')
    return return_data

