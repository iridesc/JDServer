from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):
    with open('./nohup.out') as f:
        text=f.read()

    return HttpResponse('<center><h1>what are you looking for?</h1><h2>{}</h2></center>'.format(text))


