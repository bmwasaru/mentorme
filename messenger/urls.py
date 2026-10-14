from django.urls import re_path

from messenger import views

urlpatterns = [
    re_path(r'^$', views.inbox, name='inbox'),
    re_path(r'^new/$', views.new, name='new_message'),
    re_path(r'^send/$', views.send, name='send_message'),
    re_path(r'^delete/$', views.delete, name='delete_message'),
    re_path(r'^users/$', views.users, name='users_message'),
    re_path(r'^check/$', views.check, name='check_message'),
    re_path(r'^(?P<username>[^/]+)/$', views.messages, name='messages'),
]
