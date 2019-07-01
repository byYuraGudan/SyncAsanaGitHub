
from django.urls import path,include
from django.conf.urls import url
from syncAsanaGitHub import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^github/',views.github_webhooks,name='github'),
    url(r'^asanawebhooks/$', views.asana_webhooks, name='asanawebhooks'),
]