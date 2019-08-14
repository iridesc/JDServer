import json


shopids = json.load(open('shopid.json'))
n=0
for i in shopids:
    if n != 0 and n != len(shopids):
        if i-shopids[n-1]>300:
            print(shopids[n-1],'  ',i)
    n+=1