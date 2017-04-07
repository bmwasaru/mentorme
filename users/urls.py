from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    url(r'^mentee/signup/$', mentee_signup, name='mentee_signup'),
    url(r'^mentor/signup/$', mentor_signup, name='mentor_signup'),
    # url(r'^ajax/validate_username/$', validate_username, name='validate_username'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'user/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': 'login'}, name='logout'),
]
