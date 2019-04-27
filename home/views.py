from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):
    with open('./nohup.out') as f:
        lines=f.readlines()
    html=''
    for line in lines:
        html+='<ol>{}</ol>'.format(line)
    return HttpResponse('<center><h1>Log is Here</h1></center><h6>{}</h6>'.format(html))


