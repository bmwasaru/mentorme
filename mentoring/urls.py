from django.urls import re_path
from django.views.decorators.cache import cache_page
from mentoring import views

urlpatterns = [
    re_path(r'^$', views.mentoring, name='mentoring'),
    re_path(r'^connections/$', views.connections, name='connections'),
    re_path(r'^connect/$', views.make_connection, name='make_connection'),
    re_path(r'^requests/(?P<pk>\d+)/respond/$', views.respond_connection, name='respond_connection'),
    re_path(r'^inbox/$', views.u_inbox, name='u_inbox'),
    re_path(r'^(?P<username>[\w@.-]+)/$', views.u_profile, name='u_profile'),
    # re_path(r'^(?P<username>[\w@.-]+)/$', cache_page(60 * 15)(views.u_profile), name='u_profile'),
    # re_path(r'^(?P<username>[^/]+)/$', views.u_messages, name='u_messages'),
]
