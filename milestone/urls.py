from django.conf.urls import url

from milestone import views

urlpatterns = [
    url(r'^add/$', views.add, name='add'),
    
    # url(r'^<int:todolist_id>/$', views.todolist, name='todolist'),

    # url(r'^new/$', views.new_todolist, name='new_todolist'),
    # url(r'^add/$', views.add_todolist, name='add_todolist'),
    # url(r'^add/<int:todolist_id>/$', views.add_todo, name='add_todo'),
    # url(r'^todolists/$', views.overview, name='overview'),

    url(r'^$', views.index, name='index'),
]