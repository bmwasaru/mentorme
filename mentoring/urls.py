from django.conf.urls import url
from django.views.decorators.cache import cache_page
from mentoring import views


urlpatterns = [
	url(r'^$', views.mentoring, name='mentoring'),
    url(r'^request/$', views.request_mentorship, name='request_mentorship'),
    url(r'^connect/$', views.make_connection, name='make_connection'),
    url(r'^inbox/$', views.u_inbox, name='u_inbox'),
    url(r'^(?P<username>[\w@.-]+)/$', views.u_profile, name='u_profile'),
    # url(r'^(?P<username>[\w@.-]+)/$', cache_page(60 * 15)(views.u_profile), name='u_profile'),
    # url(r'^(?P<username>[^/]+)/$', views.u_messages, name='u_messages'),
]