from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
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
    url(r'^admin/', admin.site.urls),
    url(r'^$', cache_page(CACHE_TTL)(core_views.home), name='home'),
    url(r'^mentors/$', core_views.mentors, name='mentors'),
    url(r'^mentees/$', core_views.mentees, name='mentees'),
    url(r'^setup/$', core_views.initial_setup, name='initial_setup'),
    # url(r'personality_test/$', 
    #     core_views.personality_test_view, name = 'personality'),

    # url(r'^index/$', core_views.index, name='index'),   

    # User URLs
    url(r'^account/login',
        auth_views.auth_login, {'template_name': 'core/cover.html'},
        name='login'),
    url(r'^account/logout',
        auth_views.auth_logout, {'next_page': '/'},
        name='logout'),
    url(r'^account/signup/$', mentor_auth_views.signup, name='signup'),
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
    url(r'^articles/', include('articles.urls')),
    url(r'^u/(?P<username>[\w@.-]+)/$', core_views.profile, name='profile'),

    url(r'^api/', include('api.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),

]

urlpatterns += [
    url(r'^milestone/', include('milestone.urls')),
]

urlpatterns += [
    url(r'^mentoring/', include('mentoring.urls')),
]

admin.site.site_title = 'MentorMe Adminstration'
admin.site.site_header = 'MentorMe Adminstration'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
