from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core import views as core_views
from authentication import views as mentor_auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', core_views.home, name='home'),
    url(r'^mentors/$', core_views.mentors, name='mentors'),
    url(r'^login', auth_views.login, {'template_name': 'core/cover.html'},
        name='login'),
    url(r'^logout', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/$', mentor_auth_views.signup, name='signup'),
    url(r'^settings/$', core_views.settings, name='settings'),
    url(r'^(?P<username>[^/]+)/$', core_views.profile, name='profile'),
    url(r'^settings/password/$', core_views.password, name='password'),
]

admin.site.site_title = 'Mentor001 Adminstration'
admin.site.site_header = 'Mentor001 Adminstration'
