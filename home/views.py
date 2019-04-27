from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):
    with open('./nohup.out') as f:
        text=f.read()

    return HttpResponse('<center><h1>Log is Here</h1></center><h6>{}</h6>'.format(text))


