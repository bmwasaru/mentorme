from django.urls import re_path

from milestone import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
]
