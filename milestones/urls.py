from django.conf.urls import url

from milestones import views

urlpatterns = [
    url(r'^$', views.milestones, name='milestones'),
    url(r'^completed/$', views.completed, name='completed'),
    url(r'^pending/$', views.pending, name='pending'),
    url(r'^all/$', views.all_milestones, name='all_milestones'),
    url(r'^add/$', views.add, name='add'),
]
