from django.conf.urls import url

from interests import views

urlpatterns = [
    url(r'^$', views.interests, name='interests'),
    url(r'^add/$', views.add_interest, name='add_interest'),
]
