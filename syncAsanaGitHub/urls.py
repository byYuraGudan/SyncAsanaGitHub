
from django.urls import path,include
from django.conf.urls import url
from syncAsanaGitHub import views

urlpatterns = [
    url(r'^hello/$', views.hello, name='hello'),
    path('',views.index,name='index'),
    url(r'^asana/$', views.asana, name='asana')
]