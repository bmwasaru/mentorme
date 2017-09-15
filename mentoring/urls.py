from django.conf.urls import url

from mentoring import views


urlpatterns = [
	url(r'^$', views.mentoring, name='mentoring'),
    url(r'^request/$', views.request_mentorship, name='request_mentorship'),
    url(r'^u_inbox/$', views.u_inbox, name='u_inbox'),
    url(r'^(?P<username>[\w@.-]+)/$', views.u_profile, name='u_profile'),
]