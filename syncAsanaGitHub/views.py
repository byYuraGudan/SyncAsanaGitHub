from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def hello(request):
    return HttpResponse('pong')


def index(request):
    return  HttpResponse('Hello, world. You`are at the sync index')