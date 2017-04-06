from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import mentee_signup, activate, account_activation_sent

urlpatterns = [
    url(r'^mentee/signup/$', mentee_signup, name='mentee_signup'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'user/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': 'login'}, name='logout'),
    url(r'^account_activation_sent/$', account_activation_sent,
        name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
]
