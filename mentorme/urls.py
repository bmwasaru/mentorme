from django.urls import re_path, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from core import views as core_views
from mentoring import views as mentoring_views
from authentication import views as mentor_auth_views
from activities import views as activities_views
from search import views as search_views

from django.conf import settings
from django.conf.urls.static import static

from django.views.decorators.cache import cache_page

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', cache_page(CACHE_TTL)(core_views.home), name='home'),
    re_path(r'^mentors/$', core_views.mentors, name='mentors'),
    re_path(r'^mentees/$', core_views.mentees, name='mentees'),
    re_path(r'^setup/$', core_views.initial_setup, name='initial_setup'),
    # re_path(r'personality_test/$',
    #     core_views.personality_test_view, name = 'personality'),

    # re_path(r'^index/$', core_views.index, name='index'),

    # User URLs
    re_path(r'^account/login/$',
        LoginView.as_view(template_name="core/cover.html"),
        name='login'),
    re_path(r'^account/logout/$',
        LogoutView.as_view(next_page='/'),
        name='logout'),
    re_path(r'^account/signup/$', mentor_auth_views.signup, name='signup'),
    re_path(r'^account/verify/$', mentor_auth_views.verify_account, name='verify_account'),
    re_path(r'^settings/$', core_views.settings, name='settings'),
    re_path(r'^settings/password/$', core_views.password, name='password'),
    re_path(r'^questions/', include('questions.urls'), name='questions'),
    re_path(r'^messages/', include('messenger.urls')),
    re_path(
        r'^notifications/$',
        activities_views.notifications,
        name='notifications'),
    re_path(
        r'^notifications/last/$',
        activities_views.last_notifications,
        name='last_notifications'),
    re_path(
        r'^notifications/check/$',
        activities_views.check_notifications,
        name='check_notifications'),
    re_path(r'^notifications/read-all/$', activities_views.mark_all_read, name='mark_all_notifications_read'),
    re_path(r'^notifications/(?P<pk>\d+)/open/$', activities_views.open_notification, name='open_notification'),
    re_path(r'^notifications/(?P<pk>\d+)/read/$', activities_views.mark_notification_read, name='mark_notification_read'),
    re_path(r'^search/$', search_views.search, name='search'),
    re_path(r'^articles/', include('articles.urls')),
    re_path(r'^u/(?P<username>[\w@.-]+)/$', core_views.profile, name='profile'),

    re_path(r'^api/', include('api.urls')),
    re_path(r'^api-auth/', include('rest_framework.urls')),

]

urlpatterns += [
    re_path(r'^milestone/', include('milestone.urls')),
]

urlpatterns += [
    re_path(r'^mentoring/', include('mentoring.urls')),
]

admin.site.site_title = 'MentorMe Administration'
admin.site.site_header = 'MentorMe Administration'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns = [
                      re_path(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
