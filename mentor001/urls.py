from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core import views as core_views
from authentication import views as mentor_auth_views
from activities import views as activities_views
from search import views as search_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', core_views.home, name='home'),
    url(r'^mentors/$', core_views.mentors, name='mentors'),
    url(r'^mentees/$', core_views.mentees, name='mentees'),
    url(r'^setup/$', core_views.initial_setup, name='initial_setup'),
    url(r'^education/$', core_views.education, name='education'),
    url(r'^experience/$', core_views.experience, name='experience'),
    url(r'^mentorship_areas/$', core_views.mentorship_areas, name='mentorship_areas'),
    # User URLs
    url(
        r'^account/login',
        auth_views.login, {'template_name': 'core/cover.html'},
        name='login'),
    url(
        r'^account/logout',
        auth_views.logout, {'next_page': '/'},
        name='logout'),
    url(r'^account/signup/$', mentor_auth_views.signup, name='signup'),
    url(r'^account/forgot_pass/$', mentor_auth_views.forgot_password, name="forgot_password"),
    url(r'^account/forgot_pass_confirm/$',mentor_auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^account/password_reset/(?P<id>[\d+])/$', mentor_auth_views.password_reset, name='password_reset'),
    url(r'^settings/$', core_views.settings, name='settings'),
    url(r'^settings/password/$', core_views.password, name='password'),
    url(r'^questions/', include('questions.urls'), name='questions'),
    url(r'^messages/', include('messenger.urls')),
    url(
        r'^notifications/$',
        activities_views.notifications,
        name='notifications'),
    url(
        r'^notifications/last/$',
        activities_views.last_notifications,
        name='last_notifications'),
    url(
        r'^notifications/check/$',
        activities_views.check_notifications,
        name='check_notifications'),
    url(r'^search/$', search_views.search, name='search'),
    url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
    url(r'^u/(?P<user>[\w@.-]+)/$', core_views.profile, name='profile'),
]

urlpatterns += [
    url(r'^milestones/', include('milestones.urls')),
]

admin.site.site_title = 'Mentor001 Adminstration'
admin.site.site_header = 'Mentor001 Adminstration'
