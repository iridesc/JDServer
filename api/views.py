from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseNotAllowed,HttpResponseBadRequest#引入响应类
import json,time
from api.models import TryActivity,Shop

# Create your views here.

def distributor(request):
    data=json.loads(request.body)
    Reason=data['Reason']

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
    else:
        return_data={}

    return JsonResponse(return_data)


def GetTryData(data):
    # data={
    #     'Reason':'GetTryData',
    #     'Days':1,
    # }
    if TryActivity.objects.order_by('-UpdateTime')[0].UpadateTime<time.time()-12*60*60:
        return_data={
            'Status':False,
            'Because':'TryDataTimeout'
        }
    else:
        activity_list=TryActivity.objects.filter(EndTime_gt=time.time()).filter(EndTime_lt=time.time()+data['Days']*24*60*60)
        return_data={
            'Status':True,
            'ActivityList':activity_list
        }

    return return_data

def GetBeanData(data):
    # data={
    #     'Reason':'GetBeanData',
    #     'Days':None,
    # }

    if data['Days'] == None:
        shop_list=Shop.objects.order_by('?')[0:50].valus()
    else:
        shop_list=Shop.objects.filter(LastGotTime_gt=data['Days']*24*60*60)
    
    return_data={
        'Status':True,
        'ShopList':shop_list
    }

    
    return return_data

def UpdateTryData(data):
    # data={
    #     'Reason':'UpdateTryData',
    #     'TryActivityList':[]
    # }


    try_activity_list=data['TryActivityList']
    ready_for_save_list=[]
    shop_list=[]
    for try_activity in try_activity_list:

        shop_list.append(
                        {
                            'ShopName':try_activity['ShopName'],
                            'ShopId':try_activity['ShopId'],
                        }
                    )

                    
        if try_activity['EndTime'] > time.time():
            if not TryActivity.objects.filter(ActivityId=try_activity['ActivityId']).exists():
                # print(try_activity)
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
                    
                
            else:
                print('activity exist')
                pass
        else:
            print('activity timeout')
            pass

    TryActivity.objects.bulk_create(ready_for_save_list)
    bean_return=AddBeanData({
            'Reason':'AddBeanData',
            'ShopList':shop_list
            })
    
    return_data={
        'Status':True,
        'SavedAmount':len(ready_for_save_list),
        'SavedRate':len(ready_for_save_list)/len(try_activity_list),
        'AbountBean':bean_return,
    }

    return return_data

def AddBeanData(data):

    # data={
    #     'Reason':'AddBeanData',
    #     'ShopList':[]
    # }
    
    shop_list=data['ShopList']
    
    ready_for_save_list=[]
    for shop in shop_list:
        if shop['ShopId']!='':
            if not Shop.objects.filter(ShopId=shop['ShopId']).exists():
                ready_for_save_list.append(
                    Shop(
                        ShopId = shop['ShopId'],
                        ShopnName = shop['ShopName'],
                    )
                )
            else:
                print('shop exits')
    
    Shop.objects.bulk_create(ready_for_save_list)

    return_data={
        'Status':True,

        'SavedAmount':len(ready_for_save_list),
        'SavedRate':len(ready_for_save_list)/len(shop_list),
        
    }
    return return_data


def UpdateBeanData(data):
        pass
        return {}
