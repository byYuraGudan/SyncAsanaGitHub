
from django.urls import path,include
from django.conf.urls import url
from syncAsanaGitHub import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^github/',views.hello,name='github'),
    url(r'^asanawebhooks/$', views.asana_subscribe_webhooks, name='asanawebhooks'),
]