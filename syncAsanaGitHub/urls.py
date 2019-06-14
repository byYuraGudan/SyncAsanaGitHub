
from django.urls import path,include
from django.conf.urls import url
from syncAsanaGitHub import views

urlpatterns = [
    url(r'^api/hello/$', views.hello, name='hello'),
]