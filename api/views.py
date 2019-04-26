from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseNotAllowed,HttpResponseBadRequest#引入响应类
import json,time
from api.models import TryActivity,Shop

# Create your views here.

def distributor(request):
    try:
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
        elif Reason == 'Operator':
            return_data=Operator(data)
            
        else:
            return_data={
                'Status':False,
                'Reason':'Unknow optation'
                }
    except:
        return_data={
            'Status':False,
            'Reason':'Hi There!'
            }

    return JsonResponse(return_data)


def GetTryData(data):
    # data={
    #     'Reason':'GetTryData',
    #     'Days':1,
    # }
    if TryActivity.objects.order_by('-UpdateTime')[0].UpdateTime<time.time()-12*60*60:
        return_data={
            'Status':False,
            'Because':'TryDataTimeout'
        }
    else:
        activity_list=list(
            TryActivity.objects.filter(EndTime__gt=time.time())\
            .filter(EndTime__lt=time.time()+data['Days']*24*60*60).values()
        )
        return_data={
            'Status':True,
            'TryActivityList':activity_list
        }

    return return_data

def GetBeanData(data):
    # data={
    #     'Reason':'GetBeanData',
    #     'Days':None,
    # }

    if data['Days'] == 0:
        shop_list=list(Shop.objects.order_by('?')[0:50].values())
    else:
        shop_list=list(Shop.objects.filter(LastGotTime__gt=data['Days']*24*60*60).values())
    
    return_data={
        'Status':True,
        'ShopList':shop_list
    }

    
    return return_data

def UpdateTryData(data):
    TryActivity.objects.all().delete()

    # data={
    #     'Reason':'UpdateTryData',
    #     'TryActivityList':[]
    # }


    try_activity_list=[]
    for_unique=[]
    for activity in data['TryActivityList']:
        if activity['ActivityId'] not in for_unique:
            for_unique.append(activity['ActivityId'])
            try_activity_list.append(activity)

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
                    
                # print('add')
            else:
                # print('activity exist')
                pass
        else:
            #print('activity timeout')
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
        'AboutBean':bean_return,
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
                #print('shop exits')
                pass
    
    Shop.objects.bulk_create(ready_for_save_list)

    return_data={
        'Status':True,

        'SavedAmount':len(ready_for_save_list),
        'SavedRate':len(ready_for_save_list)/len(shop_list),
        
    }
    return return_data

def UpdateBeanData(data):
    # data={
    #     'Reason':'UpdateBeanData',
    #     'ShopList':[]
    # }
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
        'UpdatedRate':n/len(shop_list),
        'ErrorList':error_list,
    }
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